from . import symbol_factory as SF
from . import enum_factory as EF

root_symbol = SF.Symbol('symbol')
SF.register_symbols_at_target(root_symbol, '''

	miss
	empty
	not_set
	copy
	end_of_pattern
	unresolved

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

	action.raise_exception
	action.default
	action.skip
	action.sub_dispatcher

	action.exit_sub_parser
	action.yield_match
	action.yield_token
	action.yield_text

	mnemonic.context.manipulation.discard_entry
	mnemonic.context.manipulation.new_context

	aggregator.status.Pending
	aggregator.status.Working
	aggregator.status.Finished
	aggregator.status.Aborted

	state_management.any_state


''')

EF.convert_symbol_to_enum(root_symbol.indention.mode)
EF.convert_symbol_to_enum(root_symbol.aggregator.status)

