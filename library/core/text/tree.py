from ..symbol import Enum
from .. import record as R
from . import Immutable_Line_View

#This is specifically for dealing with a line view as a tree
#This should replace the current trees we have but we also need a mutable tree
#So we will leave the old stuff in there til we have fixed this

Tree_Node_Classification = Enum('Tree_Node_Classification',
	'Empty',
	'Malformed_Tree',
	'Malformed_Node',
	'Tree',
	'Node',
	'Unclassified',
)



class Tree_State_Configuration(R.Record):
	'Configuration for tree behavior'
	#TODO - these things are not implemented yet
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
	start: R.Field()
	length: R.Field()

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
	def title_text(self):
		return self.state.source[self.start].text

	@property
	def title_line(self):
		return self.state.source[self.start]

	@property
	def title_indent(self):
		return self.state.source[self.start].indent

	@property
	def classification(self):

		#Flags
		empty = self.is_empty
		malformed = self.skipped_indention_level > 0
		title = bool(self.title)
		node_count = self.count_tree_nodes()

		#TODO - use enumerator symbols
		if empty:
			return Tree_Node_Classification.Empty
		elif malformed and node_count > 1:
			return Tree_Node_Classification.Malformed_Tree
		elif malformed and node_count == 1:
			return Tree_Node_Classification.Malformed_Node
		elif (not title) or (node_count > 1):
			return Tree_Node_Classification.Tree
		elif title and (node_count == 1):
			return Tree_Node_Classification.Node
		else:
			return Tree_Node_Classification.Unclassified

	@classmethod
	def from_str(cls, text):
		return cls.from_line_view(Immutable_Line_View.from_str(text))

	@classmethod
	def from_lines(cls, lines):
		return cls.from_line_view(Immutable_Line_View.from_lines(lines))

	@classmethod
	def from_empty_line_count(cls, count):
		return cls.from_line_view(Immutable_Line_View.from_str('\n'*count))

	@classmethod
	def from_fragments(cls, fragments):
		c_fragments = list()
		for frag in fragments:	#NOTE - uggly hack for now - we should have a unified interface for these trees
			if isinstance(frag, cls):
				c_fragments.append(frag.state.source)
			else:
				c_fragments.append(frag)
		return cls.from_line_view(Immutable_Line_View.from_fragments(c_fragments))

	@classmethod
	def from_title_and_body(cls, title, body):

		c_body = list()
		for frag in body:	#NOTE - uggly hack for now - we should have a unified interface for these trees
			if isinstance(frag, cls):
				c_body.append(frag.state.source)
			else:
				c_body.append(frag)



		return cls.from_line_view(Immutable_Line_View.from_title_and_body(title, c_body))

	@classmethod
	def from_line_view(cls, view, **config_options):
		config = Tree_State_Configuration(**config_options)
		return cls(Tree_State(view, config), start=0, length=len(view))

	def indented(self, adjustment=1, normalized_indention=False):
		return type(self).from_line_view(self.state.source[self.start:self.start+self.length].indented(adjustment, normalized_indention))

	def iter_lines(self, only_with_content=False):
		if only_with_content:
			yield from ((index, line) for (index, line) in enumerate(self.state.source[self.start:self.start + self.length], self.start) if line.value.strip())
		else:
			yield from enumerate(self.state.source[self.start:self.start + self.length], self.start)

	def to_str(self):
		return '\n'.join(line.to_str() for (index, line) in self.iter_lines())

	def compute_min_indention_level(self):
		lines = tuple(line.indent for (index, line) in self.iter_lines(True))
		return min(lines) if lines else None

	def iter_nodes(self):
		if (base_indent := self.compute_min_indention_level()) is None:
			yield self	#TODO - is this correct?
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


	def __iter__(self):
		yield from self.state.source[self.start:self.start+self.length]

	def __len__(self):
		return self.length

	def __getitem__(self, index_or_slice):
		if isinstance(index_or_slice, slice):
			return type(self).from_lines(self.state.source)
		else:
			return self.state.source[index_or_slice]

	@property
	def body(self):
		if self.title and self.length:
			if length := self.length - 1:
				return Tree_Node(self.state, start=self.start+1, length=length)


	def __repr__(self):
		return f'<{type(self).__qualname__} title={self.title!r} length={self.length}{"" if self.body else " EMPTY"}>'
