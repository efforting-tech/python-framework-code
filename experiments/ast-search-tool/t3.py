#This is an experiment in marking up an ast tree (our own take on asttokens)

from types1 import *
import ast
import tokenize
import token

#TODO - put somewhere? Maybe useful?
class LinesIO:
	def __init__(self, lines):
		self.lines = lines
		self.index = 0

	def readline(self):
		if self.index < len(self.lines):
			line = self.lines[self.index]
		else:
			return ''

		self.index += 1
		if self.index < len(self.lines):
			return f'{line}\n'
		else:
			return f'{line}'


def get_line_offset_map(lines):
	line_offset = dict()
	offset = 0
	for row, line in enumerate(lines, 1):
		line_offset[row] = offset
		offset += len(line) + 1

	return line_offset


from efforting.mvp4.text_nodes import text_node


class source_code(public_base):
	module_info = RTS.positional()
	text_node = RTS.state()
	line_offset = RTS.state()
	token_markings = RTS.state()
	ast_markings = RTS.state()

	#token_by_start = RTS.factory(dict)	#Cached lookup since most ast nodes will align with a token. Exceptions are f-strings

	@RTS.initializer
	def load_source(self):
		self.text_node = text_node.from_text(self.module_info.source)

	#TODO - maybe this should be part of textnode? Maybe this should utilize the cache feature
	@RTS.initializer
	def create_offset_map(self):
		self.line_offset = get_line_offset_map(self.text_node.lines)

	@RTS.initializer
	def mark_tokens(self):
		self.token_markings = tuple((self.offset_from_o_row_and_z_col(*t.start), self.offset_from_o_row_and_z_col(*t.end), t.type) for t in tokenize.generate_tokens(iter(self).__next__))

	@RTS.initializer
	def mark_ast(self):
		gen = ((self.offset_from_ast_node_start(item), self.offset_from_ast_node_end(item), item) for item in ast.walk(self.module_info.ast))
		self.ast_markings = tuple((start, end, item) for (start, end, item) in gen if start is not None and end is not None)

	def __iter__(self):
		num_lines = len(self.text_node.lines)
		for index, line in enumerate(self.text_node.lines, 1):
			if index < num_lines:
				yield f'{line}\n'
			else:
				yield line	#This is the last line

	def offset_from_o_row_and_z_col(self, o_row, z_col):
		return self.line_offset[o_row] + z_col

	def offset_from_ast_node_start(self, node):
		if hasattr(node, 'lineno'):
			return self.offset_from_o_row_and_z_col(node.lineno, node.col_offset)

	def offset_from_ast_node_end(self, node):
		if hasattr(node, 'end_lineno'):
			return self.offset_from_o_row_and_z_col(node.end_lineno, node.end_col_offset)

	def __repr__(self):
		return f'{self.__class__.__qualname__}({self.module_info.full_name!r})'


	def iter_ast_nodes_in_region(self, start, end):
		for a_start, a_end, item in self.ast_markings:
			if a_end <= start or a_start >= end:
				continue
			else:
				yield item

	def iter_ast_nodes_at_location(self, loc):
		for a_start, a_end, item in self.ast_markings:
			if a_start <= loc < a_end:
				yield item

	def get_token_at_location(self, loc):
		for t_start, t_end, t_type in self.token_markings:
			if t_start <= loc < t_end:
				return t_type

	def full_iteration(self):
		previous_pos = 0
		code = self.module_info.source
		for token_start, token_end, token_type in self.token_markings:
			if previous_tail := code[previous_pos:token_start]:
				yield previous_pos, token_start, previous_tail, None, tuple(self.iter_ast_nodes_in_region(previous_pos, token_start))

			yield token_start, token_end, code[token_start:token_end], token_type, tuple(self.iter_ast_nodes_in_region(token_start, token_end))

			previous_pos = token_end

	def unparse_ast_node(self, node):
		return self.module_info.source[self.offset_from_ast_node_start(node):self.offset_from_ast_node_end(node)]

	def span_from_ast__node(self, node):
		return self.offset_from_ast_node_start(node),self.offset_from_ast_node_end(node)

MD = module_directory.from_package_name('efforting.mvp4')
rts = MD.modules['efforting.mvp4.exceptions']
source = source_code(rts)

#print(source.ast_markings)


#print(source.module_info.ast.body[-1].body[-1].body[0].value)
#print(source.offset_from_ast_node_start( source.module_info.ast.body[-1].body[-1].body[0].value ) )
#print(source.offset_from_ast_node_end( source.module_info.ast.body[-1].body[-1].body[0].value ) )

#exit()

def keep_last(generator):
	item = None
	for item in generator:
		pass
	return item

colors = dict(
	Constant = (200, 250, 200),
	Name = (100, 100, 255),
	Attribute = (255, 200, 100),
	Call = (255, 150, 255),
	Assign = (255, 150, 255),
	FunctionDef = (200, 255, 200),
	ClassDef = (255, 255, 255),
	keyword = (200, 255, 255),
	arg = (200, 255, 255),
	Return = (255, 255, 255),
	NoneType = (100, 150, 100),
	ImportFrom = (255, 155, 100),
	Import = (255, 155, 100),
	alias = (255, 255, 100),
)

# for start, end, chunk, token_type, ast_nodes in source.full_iteration():
# 	if start != 478:
# 		continue

# 	# print(start, end, repr(chunk), token.tok_name.get(token_type, 'N/A'), ast_nodes)

# 	# for n in ast_nodes:
# 	# 	print(n)
# 	# 	print(source.span_from_ast__node(n), repr(source.unparse_ast_node(n)))


IGNORE = object()
PER_AST = object()

colors_by_token = {
	token.STRING: PER_AST,
	token.OP: (255, 100, 255),
	#token.NAME: (100, 100, 255),
	token.NAME: PER_AST,
	token.COMMENT: (50, 150, 50),

	None: IGNORE,
	token.NL: IGNORE,
	token.NEWLINE: IGNORE,
	token.INDENT: IGNORE,
}



print(tuple(source.iter_ast_nodes_at_location(237)))

result = ''
for c in range(0, len(source.module_info.source)):

	#print(source.get_token_at_location(c))
	#continue

	# at = keep_last(source.iter_ast_nodes_in_region(c, c+1))
	# r, g, b = colors.get(at.__class__.__name__, (200, 200, 200))

	# if (r, g, b) == (200, 200, 200):
	# 	print(at.__class__.__name__)

	r, g, b = 200, 200, 200

	token_type = source.get_token_at_location(c)
	if color := colors_by_token.get(token_type):
		if color is IGNORE:
			pass
		elif color is PER_AST:
			at = keep_last(source.iter_ast_nodes_at_location(c))

			match at:
				case ast.ClassDef():
					print(token_type)


			r, g, b = colors.get(at.__class__.__name__, (255, 255, 255))
		else:
			r, g, b = color

	else:
		print(token.tok_name.get(token_type, f'Unknown: {token_type!r}'))


	result += f'\033[38;2;{r};{g};{b}m'
	result += source.module_info.source[c]  #.replace('\t', '    ')	#Not proper tab expansion

print(result + '\033[0m')

#print(source.offset_from_ast_node_start( source.module_info.ast.body[-1].body[-1].body[0].value ) )
#print(source.offset_from_ast_node_end( source.module_info.ast.body[-1].body[-1].body[0].value ) )


#print(source.ast_markings)
#from io import StringIO
#for t in tokenize.generate_tokens(StringIO('class thing:\n\tpass').readline):
	#print(t)