from . import symbol_factory as _SF
from . import enum_factory as _EF

_root =_SF.Symbol(__name__.rsplit('.')[-1])
_root._set_auto_graft_here()
_SF.register_symbols_at_target(_root, '''

	miss

 	target.instance

	indention.mode.Tabs
	indention.mode.Spaces
	indention.mode.Custom.String
	indention.mode.Custom.Function

	argument.all.positional
	argument.all.named
	argument.positional_or_named


''')

_EF.convert_symbol_to_enum(indention.mode)

