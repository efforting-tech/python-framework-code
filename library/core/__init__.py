from .abc import A, set_qual_names

ABC = A('ABC',
	A('Factory',
		A('Contextual'),
	),
	A('Symbol'),
)

from .symbols import S, E, EM, set_enum_qual_names

set_qual_names(ABC, skip_root=True)


Symbol = S('Symbol',
	S('Not_Set'),
	S('Member',
		E('Kind',
			EM('Positional_or_Named'),	#TODO - add descriptions to these factories
			EM('Positional'),
			EM('Named'),
			EM('All_Positional'),
			EM('All_Named'),
			EM('Hierarchial'),	#TODO - what was the purpose?
		)
	),
	E('Action',
		EM('Raise_Exception'),
	),
	E('Indention_Mode',
		EM('Default'),
		EM('Spaces'),
		EM('Tabulators'),
		EM('Mixed'),
	),
)

set_enum_qual_names(Symbol, skip_root=True)
