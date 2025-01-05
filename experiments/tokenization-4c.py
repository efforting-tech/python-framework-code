from efforting.tech.template1.core.text.tokenization.block import Block
from efforting.tech.template1.core.text.tokenization.tree import Tree_Node
from efforting.tech.template1.core.table import Basic_Sequence_Table, Function_Formatter
from efforting.tech.template1.core.table.condition import Continuous_Format_And_Match_Table_Proxy

from efforting.tech.template1.core.mnemonic_language.templates import Document
from efforting.tech.template1.core.debug.socket_based_logwriter import Indented_Socket_Log_Writer
from efforting.tech.template1.core.mnemonic_language import value_to_color_spiral, freeze

from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import Symbol as S



#TODO - move into library, somewhere under data stuff
class Object_Mapping_With_Counter(R.Record):
	name_format: R.Field() = '{}'
	index: R.Field() = 0
	lut: R.Field(factory=dict)

	def format(self):
		return self.name_format.format(self.index)

	def map(self, item):
		if (existing := self.lut.get(item)) is not None:
			return existing

		result = self.lut[item] = self.format()
		self.index += 1
		return result



def create_node_table():
	node_register = Object_Mapping_With_Counter('N{}', 1)
	bt = Basic_Sequence_Table('Node Parent Title Span Level'.split())
	bt.set_column_format(0, Function_Formatter(bt, lambda c: node_register.map(c)))
	bt.set_column_format(1, Function_Formatter(bt, lambda c: '-' if c is None else node_register.map(c)))
	bt.set_column_format(2, Function_Formatter(bt, lambda c: '-' if c is None else repr(c)))
	bt.set_column_format(3, Function_Formatter(bt, lambda c: f'{c[0]}..{c[1]}'))
	bt.set_column_format(4, Function_Formatter(bt, lambda c: '-' if c is None else repr(c)))
	#bt.table_formatter.use_middle_divider = True
	return bt, node_register



#Test case 1

text = '''\
		a
	b
	c
d
'''

bt, btnr = create_node_table()

N1, N2, N3, N4, N5, N6, N7 = [object() for i in range(7)]

#			Node	Parent	Title	Span		Level
bt.add_row(	N1, 	None, 	None, 	(0, 3),		None)
bt.add_row(	N2, 	N1, 	None, 	(0, 2),		0)
bt.add_row(	N3, 	N2, 	None, 	(0, 0),		1)
bt.add_row(	N4, 	N3, 	'a', 	(0, 0),		2)
bt.add_row(	N5, 	N2, 	'b', 	(1, 1),		1)
bt.add_row(	N6, 	N2, 	'c', 	(2, 2),		1)
bt.add_row(	N7, 	N1, 	'd', 	(3, 3),		0)


bt2, bt2nr = create_node_table()
t = Continuous_Format_And_Match_Table_Proxy(bt, bt2)


dump_log = Indented_Socket_Log_Writer('localhost', 5002)
dump_log.clear()


log_table = Basic_Sequence_Table('Category Block Parent Level'.split())
log_table.set_column_format('Block', Function_Formatter(bt, lambda c: f'{c.first_line}..{c.last_line}'))
log_table.set_column_format('Parent', Function_Formatter(bt, lambda c: '-' if c is None else bt2nr.map(c)))


def log(*items):
	log_table.add_row(*items)
	dump_log.clear()
	dump_log.print(log_table.format())

def block_repr(block):
	match block:
		case tuple() | list() | set() | frozenset():
			return type(block)(map(block_repr, block))

		case Block(first_line=FL, last_line=LL):
			return f'{FL}..{LL}'

		case symbol if symbol is None:
			return '-'

		case otherwise:
			return repr(otherwise)



class Tree_Node(R.Record):
	block: R.Field(repr=lambda instance, field, info: block_repr(instance.block))	#TODO - we should use ABC to have different types of repr-functions, contextual and non contextual
	title: R.Field()	= None
	body: R.Field(factory=list)



def debug_format_line_of_tokens(document, token_list, color_function=value_to_color_spiral):
	if not token_list:
		return ''

	result = ''
	previous_position = token_list[0].match.start()

	def value_to_color(value):
		num = (sum(map(ord, repr(freeze(value)))) / 29) % 1.0
		R, G, B = color_function(num)
		return f"\033[38;2;{R};{G};{B}m"

	for t in token_list:
		t_state = dict(t.__getstate__())
		match = t_state.pop('match')
		t_state['__class__'] = type(t)
		printable = match.group().replace('\n', '↵').replace(' ', '␣').replace('\t', '↹ ')

		if (head_length := match.start() - previous_position):
			inner = document.text[previous_position:match.start()]
			result += f'\033[7;39m{inner}\033[0m'


		result += f'{value_to_color(t_state)}{printable}'
		previous_position = match.end()


	result += '\033[0m'
	return result



B = Block(Document(text))


with dump_log.indent(' '):
	for index, line in B.iter_absolute_lines(False):
		dump_log.print(f'{str(index)+":":5s}{debug_format_line_of_tokens(B, line.tokens)}')

dump_log.print()





class Block_To_Tree_Node_Translator(R.Record):
	indention_mode: R.Field() = S.Indention_Mode.Tabulators	#Note that we don't really support this yet
	debug_seen_nodes: R.Field(factory=dict)

	def compute_line_indent(self, line):
		if self.indention_mode is S.Indention_Mode.Tabulators:
			if (indent := line.indent) is not None:
				assert (level := indent.count('\t')) == len(indent)
				return level
		else:
			raise NotImplementedError()

	def hbt_split_by_indent_level(self, block, level):
		previous = None
		for index, line in block.iter_absolute_lines(True):
			if index > 0 and self.compute_line_indent(line) == level:
				yield block[previous:index]
				previous = index

		yield block[previous:]


	def translate_tree(self, block, level=0, parent=None):

		if parent is None:
			parent = Tree_Node(block)

		pieces = list(self.hbt_split_by_indent_level(block, level))

		if pieces:
			first_indent = self.compute_line_indent(pieces[0][0])
			if first_indent > level:
				head = pieces.pop(0)
				#print('We must go in', head)
				virtual = Tree_Node(head)
				parent.body.append(virtual)
				self.translate_tree(head, level+1, virtual)

			else:
				title = pieces[0][0].text.strip()
				if title:
					parent.body.append(Tree_Node(pieces.pop(0), title))
				else:
					raise NotImplementedError()

			#print('We must handle remaining pieces', pieces)
			for p in pieces:
				self.translate_tree(p, level+1, parent)

		else:
			raise NotImplementedError()


		return parent

	def old_translate_tree(self, block):
		log('translate_tree', block, None, None)

		root = Tree_Node(block)

		t.add_row(root, None, None, block.span, None)

		head = None
		body = list(self.hbt_split_by_indent_level(block, 0))
		if body and body[0] and self.compute_line_indent(body[0][0]) > 0:
			head_node = self.translate_node(body.pop(0), root, 0)
			root.body.append(head_node)

			#for child_block in body:
				#child_body = self.translate_node(child_block, root, 0)

		#print(head, body)


		return root

	def old_translate_node(self, block, parent, level):
		title = None

		log('translate_node', block, parent, level)


		if block and self.compute_line_indent(block[0]) == level:	#A title is only valid on the right level
			title = block[0].text.strip()

		node = Tree_Node(block, title)

		t.add_row(node, parent, title, block.span, level)

		head = None
		body = list(self.hbt_split_by_indent_level(block, level))

		if body and body[0] and self.compute_line_indent(body[0][0]) > level:
			head_node = self.translate_node(body.pop(0), node, level + 1)


		# #TODO - why do we need to do this?
		# if body and body[0].span == block.span:
		# 	body.pop(0)


		# if not (head or body or title):
		# 	return



		#for child_block in body:
			#child_body = self.translate_node(child_block, parent, level + 1)


			#root.body.append(head_node)


		# head = None
		# body = list(self.hbt_split_by_indent_level(block, 0))
		# if body and body[0] and self.compute_line_indent(body[0][0]) > 0:
		# 	head = body.pop(0)

		#print(head, body)
		return node


root = Block_To_Tree_Node_Translator().translate_tree(B)

print(t.tested_table.format())
print()


def dump_node(node):
	dump_log.print('NODE', node.block.span, node.title)

	with dump_log.indent():
		for sub_node in node.body:
			dump_node(sub_node)

dump_node(root)


# Output (dump_log)
# ┌────────────────┬───────┬────────┬───────┐
# │ Category       │ Block │ Parent │ Level │
# ├────────────────┼───────┼────────┼───────┤
# │ translate_tree │ 0..3  │ -      │ None  │
# │ translate_node │ 0..2  │ N1     │ 0     │
# │ translate_node │ 0..2  │ N2     │ 1     │
# └────────────────┴───────┴────────┴───────┘

# Output (stderr)
# Traceback (most recent call last):
#   File "/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-tech-template1/experiments/tokenization-4c.py", line 245, in <module>
#     root = Block_To_Tree_Node_Translator().translate_tree(B)
#   File "/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-tech-template1/experiments/tokenization-4c.py", line 188, in translate_tree
#     head_node = self.translate_node(body.pop(0), root, 0)
#   File "/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-tech-template1/experiments/tokenization-4c.py", line 216, in translate_node
#     head_node = self.translate_node(body.pop(0), node, level + 1)
#   File "/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-tech-template1/experiments/tokenization-4c.py", line 210, in translate_node
#     t.add_row(node, parent, title, block.span, level)
#     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/devilholk/.local/lib/python3.13/site-packages/efforting/tech/template1/core/table/condition.py", line 38, in add_row
#     self.test()
#     ~~~~~~~~~^^
#   File "/home/devilholk/.local/lib/python3.13/site-packages/efforting/tech/template1/core/table/condition.py", line 49, in test
#     raise Table_Mismatch_Exception(self.expected_table, self.tested_table, row)
# efforting.tech.template1.core.table.condition.Table_Mismatch_Exception: Table mismatch detected on row 3.

# Expected table:                            Tested table:
# ┌──────┬────────┬───────┬──────┬───────┐   ┌──────┬────────┬───────┬──────┬───────┐
# │ Node │ Parent │ Title │ Span │ Level │   │ Node │ Parent │ Title │ Span │ Level │
# ├──────┼────────┼───────┼──────┼───────┤   ├──────┼────────┼───────┼──────┼───────┤
# │ N1   │ -      │ -     │ 0..3 │ -     │   │ N1   │ -      │ -     │ 0..3 │ -     │
# │ N2   │ N1     │ -     │ 0..2 │ 0     │   │ N2   │ N1     │ -     │ 0..2 │ 0     │
# │ N3   │ N2     │ -     │ 0..0 │ 1     │   │ N3   │ N2     │ -     │ 0..2 │ 1     │
# │ N4   │ N3     │ 'a'   │ 0..0 │ 2     │   └──────┴────────┴───────┴──────┴───────┘
# │ N5   │ N2     │ 'b'   │ 1..1 │ 1     │
# │ N6   │ N2     │ 'c'   │ 2..2 │ 1     │
# │ N7   │ N1     │ 'd'   │ 3..3 │ 0     │
# └──────┴────────┴───────┴──────┴───────┘





