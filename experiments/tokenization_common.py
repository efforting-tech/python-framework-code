from efforting.tech.template1.core.text.tokenization import Tokenization_Specifier
from efforting.tech.template1.core.text.tokenization import actions as A
from efforting.tech.template1.core import records as R
from efforting.tech.template1.core.text.tokenization.factory import MVP_Tokenizer_Factory
from efforting.tech.template1.core.symbols import Symbol
import math, colorsys

class Abstract_Token(R.Record):
	match: R.Field()

	@property
	def value(self):
		return self.match.group(0)

class Raw_Expression(Abstract_Token):
	pass

class Indention(Abstract_Token):
	pass

class Text(Abstract_Token):
	pass

class Escape(Abstract_Token):
	escaped: R.Field()

class Token(Abstract_Token):
	type: R.Field()

NEW_LINE = Symbol('NEW_LINE')
STATEMENT = Symbol('STATEMENT')

#This is a specification for a tokenizer
tt_common = Tokenization_Specifier('tt_common')
tt_spec = Tokenization_Specifier('tt_spec')
tt_expression = Tokenization_Specifier('tt_expression')
tt_escape = Tokenization_Specifier('tt_escape')


tt_common.register_regex_token(r'(?m:^[\t ]+)', A.Emit(A.Wrap_Match(Indention)))	#NOTE - allowing zero width matching here hangs the regex, so we will have to check lines manually
tt_common.register_regex_token(r'\n', A.Emit(A.Wrap_Match(Token, NEW_LINE)))

tt_escape.include_tokenizer(tt_common)
tt_escape.register_literal_token('<<==!', A.Emit(A.Wrap_Match(Escape, '<<==')))
tt_escape.register_literal_token('!==>>', A.Emit(A.Wrap_Match(Escape, '==>>')))
tt_escape.register_literal_token('##==!', A.Emit(A.Wrap_Match(Escape, '##==')))


tt_expression.include_tokenizer(tt_escape)
tt_expression.register_literal_token('==>>', A.Return)
tt_expression.register_default(A.Emit(A.Wrap_Match(Raw_Expression)))


tt_spec.include_tokenizer(tt_escape)
tt_spec.register_literal_token('==>>', A.Raise_Exception)
tt_spec.register_literal_token('<<==', A.Enter_Tokenizer(tt_expression, unpack=True))
tt_spec.register_literal_token('##==', A.Emit(A.Wrap_Match(Token, STATEMENT)))

tt_spec.register_default(A.Emit(A.Wrap_Match(Text)))

template_tokenizer = MVP_Tokenizer_Factory.implement_tokenizer(tt_spec)

def split_tokens_into_lines(tokens, start=0, preserve_ends=True):
	last = start
	for index, item in enumerate(tokens[start:], start):
		match item:
			case Token(type=token_type) if token_type is NEW_LINE:		#Because we match a non zero width character we can be sure that the line is at least one token in length.
				yield last, index - (0 if preserve_ends else 1)
				last = index + 1

	index += 1
	count = index - last
	if count:
		#NOTE - this logic has not been properly thought through but it works in this one instance
		#print(last, index, count)
		yield last, index - 1


def freeze(item):
	match item:
		case set():
			return frozen_set(map(freeze, item))

		case dict():	#dict does preserve insertion order so we don't reorder it
			return tuple(map(freeze, item.items()))

		case tuple():
			return tuple(map(freeze, item))

		case bytes() | str() | int() | float() | type():
			return item

		case unhandled:
			raise Exception(item)


def value_to_color_spiral(value):
	# Spiral parameters
	num_spins =3
	hue = value
	saturation = 0.6 + 0.4 * math.sin(2 * math.pi * num_spins * value)
	lightness = 0.5 + 0.3 * math.cos(2 * math.pi * num_spins * value)

	# Convert HSL to RGB
	r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation**0.4)
	return int(r * 255), int(g * 255), int(b * 255)

