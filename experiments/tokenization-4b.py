from efforting.tech.template1.core.text.tokenization.block import Block
from efforting.tech.template1.core.text.tokenization.tree import Tree_Node
from efforting.tech.template1.core.table import Basic_Dict_Table

from efforting.tech.template1.core.mnemonic_language.templates import Document
from efforting.tech.template1.core.debug.socket_based_logwriter import Indented_Socket_Log_Writer
from efforting.tech.template1.core.mnemonic_language import value_to_color_spiral, freeze

from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import Symbol as S

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



dump_log = Indented_Socket_Log_Writer('localhost', 5002)
dump_log.clear()

text = '''\
	a
b1
		c1
\t
	b2
		c2

			d
z'''


# text = '''\
# hello
# 	world
# '''


text = '''\
		a
	b
	c
d
'''



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




t = Basic_Dict_Table()




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

	def translate(self, block, level=0, parent=None):
		title = None

		if block and self.compute_line_indent(block[0]) == level:	#A title is only valid on the right level
			title = block[0].text.strip()

		head = None
		body = list(self.hbt_split_by_indent_level(block, level))
		if body and body[0] and self.compute_line_indent(body[0][0]) > level:
			head = body.pop(0)

		#TODO - why do we need to do this?
		if body and body[0].span == block.span:
			body.pop(0)

		if not (head or body or title):
			return


		child_nodes = list()

		new_node = Tree_Node(block, title, child_nodes)


		if parent is None:	#Create root node
			parent = Tree_Node(block)
			node_name = f'N{len(self.debug_seen_nodes)+1}'
			self.debug_seen_nodes[parent] = node_name

			t.add_row(
				node = node_name,
				parent = '(root)',
				block = block_repr(block),
				level = level,
				title = repr(title) if title is not None else '-',
				head = block_repr(head),
				body = block_repr(body),
			)

		parent.body.append(new_node)



		node_name = f'N{len(self.debug_seen_nodes)+1}'
		self.debug_seen_nodes[new_node] = node_name

		t.add_row(
			node = node_name,
			parent = self.debug_seen_nodes[parent] if parent else '-',
			block = block_repr(block),
			level = level,
			title = repr(title) if title is not None else '-',
			head = block_repr(head),
			body = block_repr(body),
		)

		if head:
			self.translate(head, level+1, parent=new_node)

		if body:
			for body_node in body:
				self.translate(body_node, level, parent=new_node)

		return new_node


root = Block_To_Tree_Node_Translator().translate(B)

print(t.format())


print()


def dump_node(node):
	dump_log.print('NODE', node.block.span, node.title)

	with dump_log.indent():
		for sub_node in node.body:
			dump_node(sub_node)

dump_node(root)


# for child in root.children:
# 	print(child.block.span)

# print('----')

# for child in root.children[0].children:
# 	print(child.block.span)


#print(root.title)
#print(repr(Tree_Node(B[:-1]).title))



# #Experiment in dispatching trees from tokenization-3 - we will also transfer some of the features to the library


# text = '''<<==HELLO==>> TAIL
# HEAD <<==HELLO <<==!NESTED HELLO!==>> ==>>
# ##== Statement
# 	with body
# FINAL <<==HELLO==>>'''


# text = '''\
# a
# 	b1
# 		c1
# 	b2
# 		c2
# 			d
# z
# '''

# # text = '''\
# # 	u
# # 		v
# # w
# # '''





# # def dump_tree(tree):
# # 	dump_log.print('TREE')
# # 	with dump_log.indent():
# # 		for index, child in enumerate(tree.children):

# # 			#dump_log.print(index, repr(child.text), tuple(c.title for c in child.children))
# # 			dump_node(child)

# def dump_node(node):
# 	if node.has_title:
# 		dump_log.print('NODE', debug_format_line_of_tokens(node.document, node.title_line.tokens))
# 		if node.body:
# 			with dump_log.indent():
# 				for child in node.body.children:
# 					dump_node(child)
# 	else:
# 		dump_log.print('TREE')
# 		for child in node.children:
# 			dump_node(child)

# 	# if title_line := node.title_line:
# 	# 	dump_log.print('NODE', debug_format_line_of_tokens(node.document, title_line.tokens))

# 	# 	if node.body:
# 	# 		dump_node(node.body)

# 	# else:
# 	# 	dump_tree(node)

# 		#if (body := node.body) and (node is not body):
# 			#with dump_log.indent():
# 				#dump_node(body)
# 				#dump_tree(body)

# tr = Tree_Reference(Document(text))



# #print(tr.children[0])

# #c = tr.children[0]
# #print(c.title)
# #print(c.body)

# dump_node(tr)

# #Line data
# # L: 0 'a\n'
# # L: 1 '\tb1\n'
# # L: 2 '\t\tc1\n'
# # L: 3 '\tb2\n'
# # L: 4 '\t\tc2\n'
# # L: 5 '\t\t\td\n'
# # L: 6 'z\n'



# # print(tr.children[0].title)	#a
# # print(tr.children[0].body.title)	#b1
# # print(tr.children[0].body.children[0].title)	#b1
# # print(tr.children[0].body.children[0].body.title)	#c1


# # print('---')
# # #These two both start on line 1 but one only covers the b1 node while one cover the sub tree in a
# # print(tr.children[0].body)	#Tree_Reference(document=Document(…) first_line=1 last_line=5 base_indent=1 children=(Tree_Reference(…), Tree_Reference(…)) indention_mode=Symbol.Indention_Mode:Tabulators)
# # print(tr.children[0].body.children[0])	#Tree_Reference(document=Document(…) first_line=1 last_line=2 base_indent=1 children=() indention_mode=Symbol.Indention_Mode:Tabulators)


# # Line data
# # L: 0 '\tu\n'
# # L: 1 '\t\tv\n'
# # L: 2 'w\n'

# # print(repr(tr.title))	#'u'
# # print(repr(tr.children[0].title))	#'u'
# # print(repr(tr.children[0].body.title))	#'v'
# # print(repr(tr.children[1].title))	#'w'
