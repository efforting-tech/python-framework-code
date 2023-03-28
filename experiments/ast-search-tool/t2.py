#This is an experiment in marking up an ast tree (our own take on asttokens)

from types1 import *
import ast
import tokenize
import token

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


	def full_iteration(self):

		previous_pos = 0
		code = self.module_info.source
		for token_start, token_end, token_type in self.token_markings:
			if previous_tail := code[previous_pos:token_start]:
				yield previous_pos, token_start, previous_tail, None, ()

			yield token_start, token_end, code[token_start:token_end], token_type, ()

			previous_pos = token_end


from collections import deque

from efforting.mvp4.symbols import register_multiple_symbols
LEFT, RIGHT, LEFT_OVERLAP, RIGHT_OVERLAP, INSIDE, FULL_OVERLAP, OUTSIDE = register_multiple_symbols(*'LEFT RIGHT LEFT_OVERLAP RIGHT_OVERLAP INSIDE FULL_OVERLAP OUTSIDE'.split())

#WIP - idea here is to be able to map things to regions that split up but we can do the horrible "check-every-character" for now when presenting info
class region_map(public_base):
	regions = RTS.factory(deque)

	def add_region(self, start, end, value):

		for rs, re, d in self.regions:

			if re <= start:
				overlap = LEFT
			elif rs >= end:
				overlap = RIGHT
			elif rs == start and re == end:
				overlap = FULL_OVERLAP
			elif rs <= start and re == end:
				overlap = FULL_OVERLAP
			else:
				overlap = 'unknown'


			print(rs, re, d, overlap)

		self.regions.append((start, end, value))

rm = region_map()

rm.add_region(5, 10, 'world')
#rm.add_region(5, 10, 'hel')
#rm.add_region(3, 5, 'hello')
#rm.add_region(10, 15, 'hello')
rm.add_region(6, 8, 'hello')
#rm.add_region(2, 15, 'hello')


exit()

MD = module_directory.from_package_name('efforting.mvp4')
rts = MD.modules['efforting.mvp4']
source = source_code(rts)

#print(source.ast_markings)

for start, end, chunk, token_type, ast_nodes in source.full_iteration():
	print(start, end, repr(chunk), token.tok_name.get(token_type, 'N/A'))
