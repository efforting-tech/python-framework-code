from ..processing import Type_LUT_Processor
from ..document.structures import Text_Match
from .structures import Optional, Mnemonic, Expression
from ..text.styling import Stylized_Span

from . import string_formatting_rules
from .string_formatting_rules import string_formatter

styling_processor = Type_LUT_Processor('styling_processor')

@styling_processor.register(tuple)
@styling_processor.register(Mnemonic)
def format_tuple(processor, item):
	return Stylized_Span('mnemonic', tuple(map(processor.process_item, item)))

@styling_processor.register(Text_Match)
def format_text_match(processor, item):
	return item.match.group()

@styling_processor.register(Optional)
def format_optional(processor, item):
	return Stylized_Span(None, (
		Stylized_Span('punctuation', '['),
		format_tuple(processor, item),
		Stylized_Span('punctuation', ']'),
	))

@styling_processor.register(Expression)
def format_expression(processor, item):
	return Stylized_Span(None, (
		Stylized_Span('punctuation', '{'),
		Stylized_Span('expression', string_formatting_rules.format_tuple(string_formatter, item)),
		Stylized_Span('punctuation', '}'),
	))
