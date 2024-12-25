from ... import records as R, Symbol as S
from ... debug.socket_based_logwriter import Indented_Socket_Log_Writer

log = Indented_Socket_Log_Writer('localhost', 5001)


class Tree_Node(R.Record):
	block: R.Field()

	#children: R.Field(factory='_init_children')
	indention_mode: R.Field() = S.Indention_Mode.Tabulators	#Note that we don't really support this yet - especially relating to sub nodes
	#has_title: R.Field(factory='_init_has_title') = S.Automatic
	min_indent: R.Field(factory='_init_min_indent')	#TODO - read only

	def compute_line_indent(self, index):
		if self.indention_mode is S.Indention_Mode.Tabulators:
			line = self.block[index]
			if (indent := line.indent) is not None:
				assert (level := indent.count('\t')) == len(indent)
				return level
		else:
			raise NotImplementedError()

	@property
	def title(self):	#TODO - cache
		if not self.block:
			return

		body_indent = Tree_Node(self.block[1:]).min_indent
		if body_indent is not None and body_indent <= self.min_indent:	#NOTE - by definition it should not be able to be less than min_indent but we check that anyway
			return

		return self.block[0].text.strip() or None

	def _init_min_indent(self):
		min_level = None

		for index, line in self.block.iter_lines(True):
			indent = self.compute_line_indent(index)
			if min_level is None or indent < min_level:
				min_level = indent
				if min_level == 0:
					break	#Early return

		return min_level



'''

	Definitions:



'''




if False:


	class Tree_Reference(R.Record):
		document: R.Field()
		first_line: R.Field() = 0
		last_line: R.Field(factory='_init_last_line')
		base_indent: R.Field(factory='get_min_indent')	#Note that order here matters since some of these requires others
		children: R.Field(factory='_init_children')
		indention_mode: R.Field() = S.Indention_Mode.Tabulators	#Note that we don't really support this yet - especially relating to sub nodes
		has_title: R.Field(factory='_init_has_title') = S.Automatic

		@property
		def line_count(self):
			return self.last_line - self.first_line + 1

		def _init_has_title(self):
			if (self.has_title is S.Automatic) and (self.first_line <= self.last_line):
				return bool(self.document[self.first_line].text.strip())
			else:
				return False


		def _init_last_line(self):
			return len(self.document) - 1

		def _init_children(self):
			base_indent = self.base_indent

			log.print('init children', self.first_line, self.last_line, 'bi', base_indent)
			# with log.indent('    L: '):
			# 	for index, line in self.iter_lines(True):
			# 		log.print(index, repr(line.text))

			with log.indent():
				result = list()
				last_index = self.first_line
				for index, line in self.iter_lines(True):
					indent = self.compute_indent(index)
					#log.print('LINE', index, indent == base_indent, index - 1 > 0, last_index, index - 1)
					if indent == base_indent and index - 1 >= last_index:
						log.print('CHILD', index, indent == base_indent, last_index, index - 1)
						assert index - 1 >= last_index

						child = Tree_Reference(self.document, last_index, index - 1)
						result.append(child)
						last_index = child.last_line + 1

				if last_index > self.first_line:
					log.print('TAIL', last_index, self.last_line)
					child = Tree_Reference(self.document, last_index, self.last_line, has_title=False)
					result.append(child)

			return tuple(result)


			# result = list()
			# last_index = self.first_line

			# def add_chunk(index, is_last=False):
			# 	nonlocal last_index
			# 	if is_last and (last_index, index) == (self.first_line, self.last_line):
			# 		return

			# 	if is_last and last_index > index - 1:
			# 		result.append(Tree_Reference(self.document, last_index, index))
			# 	else:
			# 		if index > 0:
			# 			result.append(Tree_Reference(self.document, last_index, index-1))
			# 	last_index = index

			# for index, line in self.iter_lines(True):
			# 	indent = self.compute_indent(index)
			# 	if indent == base_indent:
			# 		add_chunk(index)

			# add_chunk(self.last_line, True)
			# return tuple(result)


		def iter_lines(self, only_with_content=False):
			for index in range(self.first_line, self.last_line + 1):
				line = self.document[index]
				if only_with_content and not line.body_span:
					continue
				yield (index, line)


		@property	#TODO - should be cached
		def body(self):
			if self.has_title:
				if self.first_line + 1 <= self.last_line:
					return Tree_Reference(self.document, self.first_line + 1, self.last_line)
			else:
				return self


		@property
		def text(self):
			return '\n'.join(l.text for i, l in self.iter_lines())

		@property
		def title(self):
			if self.has_title and (body_text := self.document[self.first_line].body_text):
				return body_text.strip()

		@property
		def title_line(self):
			if self.has_title and (body_text := self.document[self.first_line].body_text):
				return self.document[self.first_line]

		@property
		def title_indent(self):
			if self.has_title and (body_text := self.document[self.first_line].body_text):
				return compute_indent(self.first_line)


		def compute_indent(self, index):
			if self.indention_mode is S.Indention_Mode.Tabulators:
				line = self.document[index]
				if (indent := line.indent) is not None:
					assert (level := indent.count('\t')) == len(indent)
					return level
			else:
				raise NotImplementedError()

		def get_min_indent(self):
			min_level = None

			for index, line in self.iter_lines(True):
				indent = self.compute_indent(index)
				if min_level is None or indent < min_level:
					min_level = indent
					if min_level == 0:
						break	#Early return

			return min_level

