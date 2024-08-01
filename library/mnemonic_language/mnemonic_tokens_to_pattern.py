from .. import symbol
from ..document.structures import Text_Match
from ..matching import data_condition as DC
from ..processing.generic import Type_LUT_Processor, Identity_LUT_Processor
from ..processing.text_tree import Mnemonic_Text_Tree_Processor
from .rudimentary_definition_helpers import join_sequence, word, optional, literal, ws
from .structures import Optional, Mnemonic, Expression

T = symbol.text.token

mttp = Type_LUT_Processor('mttp')
tmip = Identity_LUT_Processor('tmip')
mlexp = Mnemonic_Text_Tree_Processor('mlexp')


@mlexp.register(join_sequence(ws, word('name'), require_sequence_type=Expression))
def process_expression_name(processor):
	processor.capture_meta['name'] =  'name'	#TODO - describe proper post processing here

	return word() & DC.Capture('name')

@mlexp.register(join_sequence(ws, word('pattern'), require_sequence_type=Expression))
def process_expression_name(processor):
	processor.capture_meta['pattern'] = 'pattern'	#TODO - describe proper post processing here
	return DC.Capture_Remaining('pattern')



@mttp.register(tuple)
@mttp.register(Mnemonic)
def process_tuple(processor, item):
	return DC.Type_Instance(Mnemonic) & DC.Sequence(*map(processor.process_item, item))

@mttp.register(Text_Match)
def process_text_match(processor, item):
	return tmip.process_item(item.token, item)

@tmip.register(T.word)
def process_token_word(processor, token, item):
	return word(item.match.group())

@tmip.register(T.literal)
def process_token_word(processor, token, item):
	return literal(item.match.group())

@tmip.register(T.whitespace)
def process_token_word(processor, token, item):
	return ws


@mttp.register(Optional)
def process_optional(processor, item):
	return optional(*map(processor.process_item, item))

@mttp.register(Expression)
def process_expression(processor, item):
	return mlexp().process_item(item)

