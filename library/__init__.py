from .core.symbol import Symbol as S, Enum as E
from .core.abc import ABC, ABC_Root_Node

#TODO - clean up tree, add descriptions
Symbol = S('Symbol',
	E('Action',
		'Default',
		'Raise_Exception',
	),
	S('Not_Set'),
	S('Default'),
	S('Miss'),
	S('Copy'),
	S('Target',
		S('Instance'),
	),
	S('Indention',
		E('Mode',
			'Tabs',
			'Spaces',
		)
	),
	S('Argument',
		S('Positional_or_Named'),
		S('All',
			S('Named'),
			S('Positional'),
		),
	),
	S('Member',
		E('Kind',
			'Positional_or_Named',
			'Positional',
			'Named',
			'All_Positional',
			'All_Named',
			'Internal',
			'Hierarchial',
		),
	),
	S('State_Management',
		S('Any_State'),
	),
	S('Aggregator',
		E('Status',
			'Pending',
			'Working',
			'Finished',
			'Aborted',
		),
	),
)


Symbol.Action.Default.__doc__ = 'Default action'
Symbol.Action.Raise_Exception.__doc__ = 'An exception should be raised'





if False:

	from .core.abc import ABC, ABC_Root_Node
	from .core.symbol import Symbol, Strict_Symbol, Symbol_Root_Node
	from .core.enum import convert_symbol_to_enum

	#TODO - These are just to showcase
	SYMBOL_DEFINITION = '''

		Math
			Matrix
			Vector
			Tensor

		E Aggregator.Status
			Pending
			Working
			Finished
			Aborted

		Not_Set
		Miss
		Empty

		E Action
			Raise_Exception
			Default

		E Export
			Auto
			Yes
			No

		Member
			E Kind
				Positional_or_Named
				All_Positional
				All_Named

		Type_System
			E Merge_Mode
				Replace
				Update



	'''

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


		#TODO - basic dispatcher
		#title_extractor1 = strict_regex_extractor(r'\s*(\w+)\s*(#.*)?', r'\1')
		#title_extractor2 = strict_regex_extractor(r'\s*(E)\s*(\w+)\s*(#.*)?')

		p1 = re.compile(r'\s*([\w\.]+)\s*(#.*)?')
		p2 = re.compile(r'\s*(E)\s*([\w\.]+)\s*(#.*)?')

		def parse_symbol_tree(parent, v):
			for item in v.iter_nodes():

				if m := p1.fullmatch(item.title):
					title, comment = m.groups()
					parse_symbol_tree(parent.get_or_create_by_path(title), item.body)

				elif m := p2.fullmatch(item.title):
					type_code, title, comment = m.groups()
					new_item = parent.get_or_create_by_path(title)

					if type_code == 'E':
						convert_symbol_to_enum(new_item)

					else:
						raise Exception(item)

					parse_symbol_tree(new_item, item.body)


				elif item.title:
					raise Exception(item)


				#if title := title_extractor1(item.title):
					#parse_symbol_tree(parent.get_or_create(title), item.body)


		parse_symbol_tree(Symbol_Root_Node, Immutable_Tree_View(SYMBOL_DEFINITION))


#TODO - Add the ABC tree
ABC_DEFINITION = '''

	Factory
		Contextual


'''


#Register a few base classes
ABC.String(str)

import re
ABC.Regex.Compiled(re.Pattern)

ABC.Text.Block.Immutable(str)

ABC.ID_Map(dict)	#TODO - this should actually be an id-map (keys are identifiers)

ABC.Sequence(tuple)
ABC.Sequence(list)



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
			if item.title and (title := title_extractor(item.title)):
				parse_abc_tree(parent.get_or_create(title), item.body)


	parse_abc_tree(ABC_Root_Node, Immutable_Tree_View(ABC_DEFINITION))


#load_symbols()
load_abstract_base_classes()
