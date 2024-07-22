from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M

from efforting.mvp6.str.interface import String_Interface

from efforting.mvp6.processing import LUT_Processor

from efforting.mvp6 import symbol
T = symbol.text.token


class Tokens:
	common = {
		T.word: r'\w+',
		T.whitespace: r'\s+',
		T.literal: None,
	}

	mnemonic_expression = {
		T.right_curly_bracket: r'\}',
		**common,
	}

	mnemonic = {
		T.left_curly_bracket: r'\{',
		**common,
	}


#class Parser(Structure):
#	pass


class Switchable_Iterator(Structure):
	source = M.positional()

	def __iter__(self):
		while True:
			try:
				yield next(self.source)
			except StopIteration:
				return

class Token_Parser(LUT_Processor):
	tokens = M.positional(factory=dict())

	def map_token_to_action(self, token, action):
		self.rules.map_action(token, action)

	def set_default_action(self, action):
		self.rules.default_action = action

	def process_text(self, text):
		processor_stack = [self]
		token_stream = Switchable_Iterator(String_Interface.regex_tokenize(text, processor_stack[-1].tokens))

		for token in token_stream:
			action = processor_stack[-1].rules.lookup_action(token.token, None)

			match action:
				case Enter_Sub_Parser(target):
					print('ENTER', target.name)
					processor_stack.append(target)
					token_stream.source = String_Interface.regex_tokenize(text, processor_stack[-1].tokens, token.match.end())

				case actions if action is symbol.action.exit_sub_parser:
					exited_from = processor_stack.pop(-1)
					print('EXIT', exited_from.name)
					token_stream.source = String_Interface.regex_tokenize(text, processor_stack[-1].tokens, token.match.end())

				case actions if action is symbol.action.yield_match:
					print('YIELD MATCH', repr(token.match))

				case actions if action is symbol.action.yield_token:
					print('YIELD TOKEN', repr(token))

				case nothing if nothing is None:
					print(token.token)

				case unhandled:
					raise Exception(action)


class Enter_Sub_Parser(Structure):
	sub_parser = M.positional()

tp = Token_Parser('mnemonic', tokens=Tokens.mnemonic)
subp = Token_Parser('mnemonic-expression', tokens=Tokens.mnemonic_expression)
subp.map_token_to_action(T.right_curly_bracket, symbol.action.exit_sub_parser)
subp.set_default_action(symbol.action.yield_match)
tp.map_token_to_action(T.left_curly_bracket, Enter_Sub_Parser(subp))
tp.set_default_action(symbol.action.yield_match)

test = 'hello: how-{are things}-going?'
tp.process_text(test)


exit()


tokens = Switchable_Iterator(String_Interface.regex_tokenize(test, Tokens.mnemonic))

for t in tokens:
	print(f'{t.token._name:30}{t.match.group()!r:50}{t.match}')
	if t.token is T.left_curly_bracket:
		print('== Enter ==')
		tokens.source = String_Interface.regex_tokenize(test, Tokens.mnemonic_expression, t.match.end())

	elif t.token is T.right_curly_bracket:
		print('== Exit ==')
		tokens.source = String_Interface.regex_tokenize(test, Tokens.mnemonic, t.match.end())




# def tokenize_mnemonic(mnemonic):
# 	yield from String_Interface.regex_tokenize(mnemonic, {
# 		T.left_curly_bracket: r'\{',
# 		T.word: r'\w+',
# 		T.whitespace: r'\s+',
# 		T.literal: None,
# 	})


# def tokenize_mnemonic_expression(mnemonic):
# 	yield from String_Interface.regex_tokenize(mnemonic, {
# 		T.right_curly_bracket: r'\}',
# 		T.word: r'\w+',
# 		T.whitespace: r'\s+',
# 		T.literal: None,
# 	})

