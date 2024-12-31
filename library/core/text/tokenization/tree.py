from ... import records as R, Symbol as S

#TODO - we should have a sub type for node or tree instead.
# OR .. make some predefined tests so we can see where we are going wrong - step through


class Tree_Node(R.Record):
	block: R.Field()
	min_indent: R.Field(factory='_init_min_indent')	#TODO - read only
	level: R.Field(post_process='_init_level', default=S.Automatic)
	has_title: R.Field(post_process='_init_has_title', default=S.Automatic)



	#children: R.Field(factory='_init_children')
	indention_mode: R.Field() = S.Indention_Mode.Tabulators	#Note that we don't really support this yet - especially relating to sub nodes

	def _init_level(self, value):
		if value is S.Automatic:
			return self.min_indent
		else:
			return value

	def _init_has_title(self, value):
		if value is S.Automatic:
			return self.compute_line_indent(self.block[0]) == self.level
		else:
			return value


	@classmethod
	def from_tree_block(cls, document):
		return Tree_Node(document, has_title=False)

	@classmethod
	def from_node_block(cls, document):
		return Tree_Node(document, has_title=True)

	@property
	def title(self):	#TODO - cache
		return self.has_title and self.block[0].text.strip() or None

	@property
	def title_tokens(self):	#TODO - cache
		return self.has_title and self.block[0].tokens or None

	def iter_nodes(self):
		log.print(f'iter nodes span={self.block.span} title={self.title!r} level={self.level} min_indent={self.min_indent}')

		if self.has_title:
			block = self.block[1:]
		else:
			block = self.block

		with log.indent():
			result = list()
			previous = None
			for index, line in block.iter_relative_lines(True):
				indent = self.compute_line_indent(line)
				#log.print(indent, line)

				if indent == self.level:
					if previous is None:
						if head := Tree_Node(block[:index], level=self.level + 1):
							log.print('HEAD', index, head.block.span, head.level)
							yield head
					else:
						if chunk := Tree_Node(block[previous:index], level=self.level + 1):
							log.print('CHUNK', index, chunk.block.span, chunk.level)
							yield chunk

					previous = index



			if tail_block := block[previous:]:
				tail = Tree_Node(tail_block, level=self.level + 1, has_title=True)
				log.print('TAIL', tail.block.span, tail.level)
				yield tail


				#yield Tree_Node(

		yield from ()


	# def iter_nodes(self):
	# 	base_indent = self.min_indent
	# 	log.print('iter nodes', self.block.span, 'bi', self.min_indent, self.has_title)

	# 	if self.has_title:
	# 		block = self.block[1:]
	# 		sub_indent = base_indent
	# 	else:
	# 		block = self.block
	# 		sub_indent = base_indent + 1

	# 	with log.indent():
	# 		result = list()
	# 		previous = block.first_line
	# 		for index, line in block.iter_absolute_lines(True):
	# 			indent = self.compute_line_indent(line)
	# 			if indent == base_indent:
	# 				if index and (sub_block := block.absolute_sub_block(previous, index - 1)):
	# 					log.print('SUB BLOCK', sub_block)
	# 					child = Tree_Node(sub_block, self.compute_line_indent(sub_block[0]) != sub_indent, sub_indent)
	# 					#log.print('EI',  self.compute_line_indent(sub_block[0]) == sub_indent)


	# 					yield child
	# 					previous = index

	# 		if (tail_block := block.absolute_sub_block(previous, block.last_line)):
	# 			log.print('TAIL BLOCK', tail_block)
	# 			child = Tree_Node(tail_block, self.compute_line_indent(tail_block[0]) != sub_indent, sub_indent)
	# 			yield child




	# def _init_children(self):
	# 	base_indent = self.min_indent
	# 	log.print('init children', self.block.span, 'bi', self.min_indent, self.has_title)

	# 	block = self.block[1:]

	# 	document = block.document
	# 	with log.indent():

	# 		result = list()
	# 		previous = block.first_line
	# 		for index, line in block.iter_absolute_lines(True):
	# 			indent = self.compute_line_indent(line)
	# 			log.print(index, line, indent, indent == base_indent)

	# 			if indent == base_indent:
	# 				if index and (sub_block := block.absolute_sub_block(previous, index - 1)):
	# 					log.print('SUB BLOCK', sub_block)
	# 					result.append(Tree_Node(sub_block, base_indent + 1))
	# 					previous = index

	# 		if self.has_title and previous and (tail_block := block.absolute_sub_block(previous, block.last_line)):
	# 			log.print('TAIL BLOCK', tail_block)
	# 			result.append(Tree_Node(tail_block, base_indent + 1))

	# 	return tuple(result)



	def compute_line_indent(self, line):
		if self.indention_mode is S.Indention_Mode.Tabulators:
			if (indent := line.indent) is not None:
				assert (level := indent.count('\t')) == len(indent)
				return level
		else:
			raise NotImplementedError()


	def _init_min_indent(self):
		min_level = None

		for index, line in self.block.iter_relative_lines(True):
			indent = self.compute_line_indent(line)
			if min_level is None or indent < min_level:
				min_level = indent
				if min_level == 0:
					break	#Early return

		return min_level


