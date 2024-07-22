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

	text.token.default
	text.token.text
	text.token.whitespace
	text.token.word
	text.token.literal


	text.token.left_curly_bracket
	text.token.right_curly_bracket
	text.token.colon
	text.token.left_square_bracket
	text.token.right_square_bracket
	text.token.left_double_arrows
	text.token.right_double_arrows
	text.token.left_paranthesis
	text.token.right_paranthesis

	raise_exception

	action.exit_sub_parser
	action.yield_match
	action.yield_token
	action.yield_text

''')

_EF.convert_symbol_to_enum(indention.mode)

