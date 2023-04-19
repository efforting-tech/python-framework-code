from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.bases import public_base
from efforting.mvp4.development_utils.introspection.package import load_package
from efforting.mvp4.text_nodes import text_node
import ast, tokenize, token as TT, re
import readline
from collections import defaultdict
from highlight_helper import get_highlighted_terminal_from_lines

from pathlib import Path

#This experiment loads a local dataset

class line_match(public_base):
	module = RTS.positional()
	line = RTS.positional()

	def present(self):
		print(self.module.full_name)
		print(self.module.syntax_highlighted_source[self.line-1])
		print()

class module_information(public_base):
	full_name = RTS.positional()
	path = RTS.positional()
	stat = RTS.positional()
	source = RTS.positional()
	ast = RTS.positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}({self.full_name!r})'

	# def search(self, text):
	# 	for index, line in enumerate(self.source_lines, 1):
	# 		if text in line:
	# 			yield line_match(self, index)

class extended_module_directory(public_base):
	modules = RTS.field(factory=dict)

	@classmethod
	def from_package_name(cls, pkg_name):

		pkg = load_package(pkg_name)
		module_registry = dict()
		for module in pkg.registry.values():
			module_registry[module.full_name] = extended_module_information(module.full_name, module.path, module.stat, module.source, module.ast)

		return cls(module_registry)


	def search(self, text):
		for module in self.modules.values():
			yield from module.search(text)




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


	line_offset[row + 1] = offset	#Final offset

	return line_offset



class source_information(public_base):
	text_node = RTS.state()
	line_offset = RTS.state()
	token_markings = RTS.state()
	ast_markings = RTS.state()

	_syntax_highlighted_source = RTS.state(None)



	#token_by_start = RTS.factory(dict)	#Cached lookup since most ast nodes will align with a token. Exceptions are f-strings

	@RTS.initializer
	def load_source(self):
		self.text_node = text_node.from_text(self.source)

	#TODO - maybe this should be part of textnode? Maybe this should utilize the cache feature
	@RTS.initializer
	def create_offset_map(self):
		self.line_offset = get_line_offset_map(self.text_node.lines)

	@RTS.initializer
	def mark_tokens(self):
		self.token_markings = tuple((self.offset_from_o_row_and_z_col(*t.start), self.offset_from_o_row_and_z_col(*t.end), t) for t in tokenize.generate_tokens(iter(self).__next__))

	@RTS.initializer
	def mark_ast(self):
		gen = ((self.offset_from_ast_node_start(item), self.offset_from_ast_node_end(item), item) for item in ast.walk(self.ast))
		self.ast_markings = tuple((start, end, item) for (start, end, item) in gen if start is not None and end is not None)

	@property	#TODO - caching or similar
	def syntax_highlighted_source(self):
		if (v := self._syntax_highlighted_source) is not None:
			return v

		self._syntax_highlighted_source = get_highlighted_terminal_from_lines(list(self.text_node.lines))

		return self._syntax_highlighted_source

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

	def get_bottom_ast_node_at_location(self, loc):
		return keep_last(self.iter_ast_nodes_at_location(loc))

	def search(self, text):
		for index, line in enumerate(self.text_node.lines, 1):
			if text in line:
				yield line_match(self, index)

	def extend_index(self, target_index):
		for index, (left, right, token) in enumerate(self.token_markings):
			if token.type == TT.NAME:
				target_index[token.string] += (token_reference(self, index),)

			else:
				for match in re.finditer(r'(?ai:[A-Z_])(?ui:\w*)', token.string):
					target_index[match.group(0)] += (token_reference(self, index),)

	def get_index(self):
		result = defaultdict(tuple)
		self.extend_index(result)
		return dict(result)


class token_reference(public_base):
	owner = RTS.positional()
	index = RTS.positional()


class extended_module_information(module_information, source_information):
	pass



class file_information(public_base):
	path = RTS.positional()
	source = RTS.state()
	stat = RTS.state()
	ast = RTS.state()

	@RTS.replace_initializer
	def load_source(self):
		self.source = self.path.read_text()
		self.stat = self.path.stat()
		self.ast = ast.parse(self.source)
		self.text_node = text_node.from_text(self.source)


class extended_source_information(file_information, source_information):

	# #Due to the bug outlined above
	# #TODO - maybe this should be part of textnode? Maybe this should utilize the cache feature
	# @RTS.initializer
	# def create_offset_map(self):
	# 	self.line_offset = get_line_offset_map(self.text_node.lines)

	# #Due to the bug outlined above
	# @RTS.initializer
	# def mark_tokens(self):
	# 	self.token_markings = tuple((self.offset_from_o_row_and_z_col(*t.start), self.offset_from_o_row_and_z_col(*t.end), t) for t in tokenize.generate_tokens(iter(self).__next__))

	# #Due to the bug outlined above
	# @RTS.initializer
	# def mark_ast(self):
	# 	gen = ((self.offset_from_ast_node_start(item), self.offset_from_ast_node_end(item), item) for item in ast.walk(self.ast))
	# 	self.ast_markings = tuple((start, end, item) for (start, end, item) in gen if start is not None and end is not None)



	def __repr__(self):
		return f'{self.__class__.__qualname__}({self.path!r})'



from pygments.formatters.terminal256 import EscapeSequence

EscapeSequence.escape = lambda self, attrs: f'\001\033[{";".join(attrs)}m\002' if attrs else ''

def strip_rl_wrap(t):
	in_band = True
	result = ''
	for c in t:
		if in_band and c == '\001':
			in_band = False
		elif not in_band and c == '\002':
			in_band = True
		elif in_band:
			result += c

	return result


def get_rl_wrapped_position(t, p):
	pos = 0
	in_band = True

	for i, c in enumerate(t):
		if in_band and c == '\001':
			in_band = False
		elif not in_band and c == '\002':
			in_band = True
		elif in_band:
			if pos == p:
				return i

			pos += 1

def get_rl_first_char(t):
	in_band = True
	last_outband_pos = 0
	for i, c in enumerate(t):
		if in_band and c == '\001':
			last_outband_pos = i + 1
			in_band = False
		elif not in_band and c == '\002':
			in_band = True
		elif in_band and c.strip():
			return last_outband_pos



class code_registry(public_base):
	sources = RTS.field(factory=dict)

	@classmethod
	def from_path(cls, path):

		# pkg = load_package(pkg_name)
		# module_registry = dict()
		# for module in pkg.registry.values():
		# 	module_registry[module.full_name] = extended_module_information(module.full_name, module.path, module.stat, module.source, module.ast)

		#extended_source_information(path, path.stat,
		registry = dict()
		for path in Path(path).glob('**/*.py'):
			print(path)
			try:
				registry[path] = extended_source_information(path)
			except Exception as e:
				print(e)


		return cls(registry)


if __name__ == '__main__':

	cr = code_registry.from_path('.')

	main_index = defaultdict(tuple)
	for source in cr.sources.values():
		print(f'index for {source.path}')
		source.extend_index(main_index)

	import importlib, sys


	from efforting.mvp2.python_formatting import use_colorized_traceback
	use_colorized_traceback()

	while True:
		query = input('Query codebase: ')
		print()
		try:
			import search
			importlib.reload(search)
			search.perform_search(cr, main_index, query)

		except Exception as e:
			sys.excepthook(e)

		print()




#term = sys.argv[1]


# keys = tuple(k for k in main_index.keys() if term in k.lower())
# #NOTE - Currently assumes token_reference is the only reference in the index
# for k in keys:
# 	for r in main_index[k]:
# 		tok = r.owner.token_markings[r.index][2]
# 		row, col = tok.start

# 		#print(r.owner.path)
# 		#print('\n'.join(r.owner.syntax_highlighted_source))
# 		line = r.owner.syntax_highlighted_source[row-1]
# 		inter_token_position = tok.string.lower().find(term)
# 		inpos = get_rl_wrapped_position(line, col + inter_token_position)
# 		first_char_pos = get_rl_first_char(line)
# 		floc = f'{str(r.owner.path.resolve().relative_to(base_dir))}:{row}'
# 		print(f'{floc:50}', line[first_char_pos:inpos] + EscapeSequence.escape(None, ['7']) + line[inpos:inpos+len(term)] + EscapeSequence.escape(None, ['27'])  + line[inpos+len(term):] )


