from .core.abc import ABC, ABC_Root_Node
from .core.symbol import Symbol, Symbol_Root_Node


#TODO - These are just to showcase
SYMBOL_DEFINITION = '''

	Math
		Matrix
		Vector
		Tensor

	Animal		#TODO - remove these
		Cat
		Dog


'''

#TODO - These are just to showcase
ABC_DEFINITION = '''

	Basic		#TODO - remove these
		Stuff
		Things

'''


#Register a few base classes
ABC.String(str)

ABC.Sequence(tuple)
ABC.Sequence(list)


#Register symbols
def load_symbols():
	from .core.text import Immutable_Tree_View

	#TODO - move to core string something something dark side
	import re
	class strict_regex_extractor:
		def __init__(self, pattern, format):
			self.pattern = re.compile(pattern)
			self.format = format

		def __call__(self, value):
			match = self.pattern.fullmatch(value)
			assert match

			return match.expand(self.format)

	title_extractor = strict_regex_extractor(r'\s*(\w+)\s*(#.*)?', r'\1')

	def parse_symbol_tree(parent, v):
		for item in v.iter_nodes():
			if title := title_extractor(item.title):
				parse_symbol_tree(parent.get_or_create(title), item.body)


	parse_symbol_tree(Symbol_Root_Node, Immutable_Tree_View(SYMBOL_DEFINITION))


#Register ABCs
def load_abstract_base_classes():
	#TODO - code deduplication from load_symbols
	from .core.text import Immutable_Tree_View

	import re
	class strict_regex_extractor:
		def __init__(self, pattern, format):
			self.pattern = re.compile(pattern)
			self.format = format

		def __call__(self, value):
			match = self.pattern.fullmatch(value)
			assert match

			return match.expand(self.format)

	title_extractor = strict_regex_extractor(r'\s*(\w+)\s*(#.*)?', r'\1')

	def parse_abc_tree(parent, v):
		for item in v.iter_nodes():
			if title := title_extractor(item.title):
				parse_abc_tree(parent.get_or_create(title), item.body)


	parse_abc_tree(ABC_Root_Node, Immutable_Tree_View(ABC_DEFINITION))


load_symbols()
load_abstract_base_classes()
