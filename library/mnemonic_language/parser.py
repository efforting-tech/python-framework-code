from ..text.parsing.structures import Enter_Sub_Parser
from ..text.parsing import Token_Parser
from . import tokens
from .. import symbol
from .structures import Mnemonic, Expression, Optional

T = symbol.text.token


#Maybe we should name these a bit better
tp = Token_Parser('mnemonic', tokens=tokens.mnemonic, post_processor=lambda p: Mnemonic(*p))

subp = Token_Parser('mnemonic-expression', tokens=tokens.mnemonic_expression, post_processor=lambda p: Expression(*p))
subp.map_token_to_action(T.right_curly_bracket, symbol.action.exit_sub_parser)
subp.set_default_action(symbol.action.yield_token)

optp = Token_Parser('opt-expression', tokens=tokens.opt_expression, post_processor=lambda p: Optional(*p))
optp.map_token_to_action(T.right_square_bracket, symbol.action.exit_sub_parser)
optp.set_default_action(symbol.action.yield_token)

tp.map_token_to_action(T.left_curly_bracket, Enter_Sub_Parser(subp))
tp.map_token_to_action(T.left_square_bracket, Enter_Sub_Parser(optp))
tp.set_default_action(symbol.action.yield_token)
