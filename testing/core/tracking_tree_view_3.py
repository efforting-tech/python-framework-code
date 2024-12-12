from efforting.mvp6.core import record as R
from efforting.mvp6.core.text import Immutable_Line_View

from tracking_tree_view_2 import render_non_printables

class Tree_State_Configuration(R.Record):
	'Configuration for tree behavior'
	emit_empty_nodes: R.Field() = True
	strict_mode: R.Field() = False

	#ChatGPT suggested a journal for errors which I don't think I will implement.
	#But if such feature were to be implemented I think the reference to the journal should be in this configuration object

class Tree_State(R.Record):
	'Tracks global settings and source reference for the tree.'
	source: R.Field()
	config: R.Field(factory=Tree_State_Configuration)

class Tree_Node(R.Record):
	state: R.Field()

	#TODO - title should be computed (and later cached)

	start: R.Field()
	length: R.Field()

	#TODO: Add things for empty or other classification
	skipped_indention_level: R.Field() = 0

	def count_body_nodes(self):
		return self.body.count_tree_nodes() if self.body else 0

	def count_tree_nodes(self):
		count = 0
		for i in self.iter_nodes():
			count += 1
		return count

	@property
	def is_tree(self):
		return self.count_tree_nodes() > 1

	@property
	def is_node(self):
		return self.count_tree_nodes() == 1

	@property
	def is_empty(self):
		return not self.to_str().strip()

	@property
	def title(self):
		return self.state.source[self.start].text.strip()

	@property
	def classification(self):

		#Flags
		empty = self.is_empty
		malformed = self.skipped_indention_level > 0
		title = bool(self.title)
		node_count = self.count_tree_nodes()

		#TODO - use enumerator symbols
		if empty:
			return 'EMPTY'
		elif malformed and node_count > 1:
			return 'MALFORMED-TREE'
		elif malformed and node_count == 1:
			return 'MALFORMED-NODE'
		elif (not title) or (node_count > 1):
			return 'TREE'
		elif title and (node_count == 1):
			return 'NODE'
		else:
			return 'UNCLASSIFIED'
			#raise Exception(empty, malformed, node_count)

	@classmethod
	def from_str(cls, text):
		return cls.from_line_view(Immutable_Line_View.from_str(text))

	@classmethod
	def from_line_view(cls, view, **config_options):
		config = Tree_State_Configuration(**config_options)
		return cls(Tree_State(view, config), start=0, length=len(view))

	def iter_lines(self, only_with_content=False):
		if only_with_content:
			yield from ((index, line) for (index, line) in enumerate(self.state.source[self.start:self.start + self.length], self.start) if line.value.strip())
		else:
			yield from enumerate(self.state.source[self.start:self.start + self.length], self.start)

	def to_str(self):
		return '\n'.join(line.text for (index, line) in self.iter_lines())

	def compute_min_indention_level(self):
		lines = tuple(line.indent for (index, line) in self.iter_lines(True))
		return min(lines) if lines else None

	def iter_nodes(self):
		if (base_indent := self.compute_min_indention_level()) is None:
			return

		last_index = next(self.iter_lines(False))[0]	#TODO - handle StopIteration

		def emit_chunk(index):
			nonlocal last_index
			pending_chunk = Tree_Node(self.state, start=last_index, length=index - last_index)

			last_index = index

			if (pending_level := pending_chunk.compute_min_indention_level()) is not None:
				pending_chunk.skipped_indention_level = pending_level - base_indent

			return pending_chunk

		for index, line in self.iter_lines(True):
			if not line.value.strip():
				continue

			if line.indent == base_indent:
				if pending_chunk := emit_chunk(index):
					#print('PEND', pending_chunk, repr(pending_chunk.to_str()))
					if pending_chunk.length:
						yield pending_chunk



		if pending_chunk := emit_chunk(self.start + self.length):
			#print('TAIL PEND', pending_chunk, repr(pending_chunk.to_str()))
			if pending_chunk.length:
				yield pending_chunk

	@property
	def body(self):
		if self.title:
			if length := self.length - 1:
				return Tree_Node(self.state, start=self.start+1, length=length)


root = Tree_Node.from_str('''
		Hello World!
			This is a test

	Here is another node
		With another body

	And even more
		freakin nodes
		and such!

''')


from efforting.mvp6.template_system.introspection import Indention_Wrapper, Indention_Wrapper_Context


stderr = Indention_Wrapper()
stderr_indent = Indention_Wrapper_Context(stderr)


def dump_tree(node):
	stderr.print(node, repr(node.title), node.classification)
	stderr.print(render_non_printables(node.to_str()))

	if node.is_node and node.body:
		with stderr_indent:
			for sub_node in node.body.iter_nodes():
				dump_tree(sub_node)
	elif node.is_tree:
		with stderr_indent:
			for sub_node in node.iter_nodes():
				dump_tree(sub_node)


dump_tree(root)


#OUTPUT

# Tree_Node(state=Tree_State(…) start=0 length=11 skipped_indention_level=0) '' TREE
# 001┊⏎
# 002┊╺━━╸╺━━╸Hello·World!⏎
# 003┊╺━━╸╺━━╸╺━━╸This·is·a·test⏎
# 004┊⏎
# 005┊╺━━╸Here·is·another·node⏎
# 006┊╺━━╸╺━━╸With·another·body⏎
# 007┊⏎
# 008┊╺━━╸And·even·more⏎
# 009┊╺━━╸╺━━╸freakin·nodes⏎
# 010┊╺━━╸╺━━╸and·such!⏎

#   Tree_Node(state=Tree_State(…) start=0 length=4 skipped_indention_level=1) '' MALFORMED-TREE
#   001┊⏎
#   002┊╺━━╸╺━━╸Hello·World!⏎
#   003┊╺━━╸╺━━╸╺━━╸This·is·a·test⏎

#     Tree_Node(state=Tree_State(…) start=0 length=1 skipped_indention_level=0) '' EMPTY

#     Tree_Node(state=Tree_State(…) start=1 length=3 skipped_indention_level=0) 'Hello World!' NODE
#     001┊╺━━╸╺━━╸Hello·World!⏎
#     002┊╺━━╸╺━━╸╺━━╸This·is·a·test⏎

#       Tree_Node(state=Tree_State(…) start=2 length=2 skipped_indention_level=0) 'This is a test' NODE
#       001┊╺━━╸╺━━╸╺━━╸This·is·a·test⏎

#   Tree_Node(state=Tree_State(…) start=4 length=3 skipped_indention_level=0) 'Here is another node' NODE
#   001┊╺━━╸Here·is·another·node⏎
#   002┊╺━━╸╺━━╸With·another·body⏎

#     Tree_Node(state=Tree_State(…) start=5 length=2 skipped_indention_level=0) 'With another body' NODE
#     001┊╺━━╸╺━━╸With·another·body⏎

#   Tree_Node(state=Tree_State(…) start=7 length=4 skipped_indention_level=0) 'And even more' NODE
#   001┊╺━━╸And·even·more⏎
#   002┊╺━━╸╺━━╸freakin·nodes⏎
#   003┊╺━━╸╺━━╸and·such!⏎

#     Tree_Node(state=Tree_State(…) start=8 length=1 skipped_indention_level=0) 'freakin nodes' NODE
#     001┊╺━━╸╺━━╸freakin·nodes⏎

#     Tree_Node(state=Tree_State(…) start=9 length=2 skipped_indention_level=0) 'and such!' NODE
#     001┊╺━━╸╺━━╸and·such!⏎



