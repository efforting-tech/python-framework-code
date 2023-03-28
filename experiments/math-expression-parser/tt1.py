from efforting.mvp4.symbols import register_symbol
from efforting.mvp4.text_processing.tokenization import tokenizer, yield_match


import re

def literal(x):
	return re.compile(re.escape(x))

def regex(x):
	return re.compile(x)

class CL:
	math_token = register_symbol('math.token')
	minus = math_token()
	digit = math_token()
	subscript = math_token()
	dot = math_token()
	symbol = math_token()
	space = math_token()
	equals = math_token()

	square_bracket = math_token('square_bracket')


class CLSQ:
	upper_left_hook = CL.square_bracket()
	left = CL.square_bracket()
	bottom_left_hook = CL.square_bracket()

	upper_right_hook = CL.square_bracket()
	right = CL.square_bracket()
	bottom_right_hook = CL.square_bracket()

#Note - we always yield match in this tokenizer so that we may know where things are
math_tokenizer = tokenizer('math_tokenizer',
	(literal('-'),				yield_match(CL.minus)),
	(literal('='),				yield_match(CL.equals)),
	(regex(r'\d+'),				yield_match(CL.digit)),
	(regex(r'(\w)\.(\w+)'),		yield_match(CL.subscript)),
	(literal('.'),				yield_match(CL.dot)),
	(regex(r'\w'),				yield_match(CL.symbol)),
	(regex(r'\s+'),				yield_match(CL.space)),


	(literal('⎡'),				yield_match(CLSQ.upper_left_hook)),
	(literal('⎢'),				yield_match(CLSQ.left)),
	(literal('⎣'),				yield_match(CLSQ.bottom_left_hook)),

	(literal('⎤'),				yield_match(CLSQ.upper_right_hook)),
	(literal('⎥'),				yield_match(CLSQ.right)),
	(literal('⎦'),				yield_match(CLSQ.bottom_right_hook)),

)
