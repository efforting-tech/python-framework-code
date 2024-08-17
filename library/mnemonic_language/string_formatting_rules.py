from ..processing.generic import Type_LUT_Processor
from ..document.structures import Text_Match
from .structures import Optional, Mnemonic, Expression


string_formatter = Type_LUT_Processor('string_formatter')

@string_formatter.register(tuple)
@string_formatter.register(Mnemonic)
def format_tuple(processor, item):
	return ''.join(map(processor.process_item, item))

@string_formatter.register(Text_Match)
def format_text_match(processor, item):
	return item.match.group()

@string_formatter.register(Optional)
def format_optional(processor, item):
	inner = ''.join(map(processor.process_item, item))
	return f'[{inner}]'

@string_formatter.register(Expression)
def format_expression(processor, item):
	inner = ''.join(map(processor.process_item, item))
	return f'{{{inner}}}'


#NOTE - this one was actually just a symptom of a failure to rename a captured expression
# @string_formatter.register(str)
# def format_str(processor, item):
# 	return item
