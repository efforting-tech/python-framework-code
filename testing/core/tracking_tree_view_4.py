from efforting.mvp6.core import record as R
from efforting.mvp6.core.text import Immutable_Line_View
from efforting.mvp6.core.symbol import Enum
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Dispatcher
from efforting.mvp6.core.dispatcher.rules import Unconditional_Rule, Core_Rule, Regex_Rule
from tracking_tree_view_2 import render_non_printables

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
	def from_line_view(cls, view, **config_options):
		config = Tree_State_Configuration(**config_options)
		return cls(Tree_State(view, config), start=0, length=len(view))

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


	Here is even more
		freakin nodes
		and such!

''')


import textwrap
import re
from efforting.mvp6 import ABC

class Tree_View_Regex_Rule(Core_Rule):	#TODO - override signature so we can have action in core_rule but still have regex_rule(cond, act)
	pattern: R.Field(type=ABC.Regex.Compiled)
	action: R.Field() = True

	def match(self, item):
		return self.pattern.fullmatch(item.title)


tvd = Tree_View_Dispatcher()
@tvd.register(Tree_View_Regex_Rule, re.compile('^Here is(.*)'))
def func(context, dispatcher, node, result):
	print(f'We found yet {result.value.match.group(1).strip()} with {node.count_body_nodes()} sub nodes.')
	if node.body:
		print('Here are the sub nodes:')
		for s in node.body.iter_nodes():
			print(repr(s.to_str()))
			#print(textwrap.indent(render_non_printables(s.to_str()), '  '))


class Core_Match(R.Record):
	rule: R.Field()

class Node_Classification_Match(Core_Match):
	classification: R.Field()

def represent_classification_set(self, field, info):
	inner = ', '.join(sorted(i.__name__ for i in getattr(self, field)))
	return f'{field}={{{inner}}}'

class Node_Classification_Rule(Core_Rule):
	classification_set: R.Field(repr=represent_classification_set)
	action: R.Field() = True

	def match(self, item):
		if (classification := item.classification) in self.classification_set:
			return Node_Classification_Match(self, classification)


@tvd.register(Node_Classification_Rule, {
	Tree_Node_Classification.Malformed_Tree,
	Tree_Node_Classification.Malformed_Node,
 })
def dfunc(context, dispatcher, node, result):
	print(f'Warning - skipping malformed node: {node}')





#print(dir(tvd.regulations.fallback_rule))

#print(tvd.regulations.fallback_rule.)

tvd.bound_dispatch_tree('context', root)


# from efforting.mvp6.template_system.introspection import Indention_Wrapper, Indention_Wrapper_Context
# from tracking_tree_view_2 import render_non_printables


# stderr = Indention_Wrapper()
# stderr_indent = Indention_Wrapper_Context(stderr)


# def dump_tree(node):
# 	stderr.print(node, repr(node.title), node.classification)
# 	stderr.print(render_non_printables(node.to_str()))

# 	if node.is_node and node.body:
# 		with stderr_indent:
# 			for sub_node in node.body.iter_nodes():
# 				dump_tree(sub_node)
# 	elif node.is_tree:
# 		with stderr_indent:
# 			for sub_node in node.iter_nodes():
# 				dump_tree(sub_node)


# dump_tree(root)

