from types1 import *
from efforting.mvp4.text_nodes import text_node
import ast, tokenize, token

def keep_last(generator):
	item = None
	for item in generator:
		pass
	return item

def get_line_offset_map(lines):
	line_offset = dict()
	offset = 0
	for row, line in enumerate(lines, 1):
		line_offset[row] = offset
		offset += len(line) + 1

	return line_offset




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
		self.token_markings = tuple((self.offset_from_o_row_and_z_col(*t.start), self.offset_from_o_row_and_z_col(*t.end), t) for t in tokenize.generate_tokens(iter(self).__next__))

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
		for t_start, t_end, tok in self.token_markings:
			if t_start <= loc < t_end:
				return tok


	def unparse_ast_node(self, node):
		return self.module_info.source[self.offset_from_ast_node_start(node):self.offset_from_ast_node_end(node)]

	def span_from_ast_node(self, node):
		return self.offset_from_ast_node_start(node),self.offset_from_ast_node_end(node)

	def bottom_ast_node_at_location(self, loc):
		return keep_last(self.iter_ast_nodes_at_location(loc))


def example_of_checking_first_token_in_ast():

	MD = module_directory.from_package_name('efforting.mvp4')
	rts = MD.modules['efforting.mvp4.exceptions']
	source = source_code(rts)

	x = 245
	print(source.bottom_ast_node_at_location(x))
	if (y := source.offset_from_ast_node_start(source.bottom_ast_node_at_location(x))) is not None:
		class_token = source.get_token_at_location(y)
		print(y, class_token)
		print(source.get_token_at_location(x))
		print(source.get_token_at_location(x) is class_token)


MD = module_directory.from_package_name('efforting.mvp4')
print(MD)
	#rts = MD.modules['efforting.mvp4.exceptions']
	#source = source_code(rts)
