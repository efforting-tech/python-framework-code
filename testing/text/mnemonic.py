from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M
from efforting.mvp6.str.interface import String_Interface

from efforting.mvp6.processing import LUT_Processor

from efforting.mvp6 import symbol
T = symbol.text.token


class Tokens:
	#NOTE - would be nice to first just define our token patterns, maybe using some shorthand for when we build the sub parser.
	#		alternatively we build the ruleset in an hierarchial manner
	common = {
		T.word: r'\w+',
		T.whitespace: r'\s+',
		T.literal: None,
	}

	mnemonic_expression = {
		T.right_curly_bracket: r'\}',
		**common,
	}

	opt_expression = {
		T.right_square_bracket: r'\]',
		T.left_square_bracket: r'\[',
		**common,
	}

	mnemonic = {
		T.left_curly_bracket: r'\{',
		T.left_square_bracket: r'\[',
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

class Token_Stream(Switchable_Iterator):
	text = M.positional(None)
	pending_position = M.positional(0)

class Token_Parser(LUT_Processor):
	tokens = M.positional(factory=dict())
	post_processor = M.positional(tuple)

	def map_token_to_action(self, token, action):
		self.rules.map_action(token, action)

	def set_default_action(self, action):
		self.rules.default_action = action


	def process_text(self, text, position=0):
		return self.process_token_stream(Token_Stream(None, text, position))

	def process_token_stream(self, token_stream):
		return self.post_processor(tuple(self.process_token_stream_iteratively(token_stream)))

	def process_token_stream_iteratively(self, token_stream):
		token_stream.source = String_Interface.regex_tokenize(token_stream.text, self.tokens, token_stream.pending_position)
		for token in token_stream:
			action = self.rules.lookup_action(token.token, None)
			print(self.name, token.token, action)

			match action:
				case Enter_Sub_Parser(target):
					print('ENTER', target.name)
					token_stream.pending_position = token.match.end()
					yield target.process_token_stream(token_stream)
					token_stream.source = String_Interface.regex_tokenize(token_stream.text, self.tokens, token_stream.pending_position)

				case actions if action is symbol.action.exit_sub_parser:
					print('EXIT', self.name)
					token_stream.pending_position = token.match.end()
					return

				case actions if action is symbol.action.yield_text:
					yield token.match.group()

				case actions if action is symbol.action.yield_match:
					yield token.match

				case actions if action is symbol.action.yield_token:
					yield token

				case nothing if nothing is None:
					raise Exception(token.token, token.match)	#TODO - proper exception

				case unhandled:
					raise Exception(action)


	def process_text_old(self, text):
		processor_stack = [self]
		result_stack = [list()]
		token_stream = Switchable_Iterator(String_Interface.regex_tokenize(text, processor_stack[-1].tokens))

		for token in token_stream:
			action = processor_stack[-1].rules.lookup_action(token.token, None)
			match action:
				case Enter_Sub_Parser(target):
					#print('ENTER', target.name)
					processor_stack.append(target)
					result_stack.append(list())
					token_stream.source = String_Interface.regex_tokenize(text, processor_stack[-1].tokens, token.match.end())

				case actions if action is symbol.action.exit_sub_parser:
					exited_from = processor_stack.pop(-1)
					sub_result = result_stack.pop(-1)
					result_stack[-1].append(sub_result)
					#print('EXIT', exited_from.name)
					token_stream.source = String_Interface.regex_tokenize(text, processor_stack[-1].tokens, token.match.end())

				case actions if action is symbol.action.yield_text:
					result_stack[-1].append(token.match.group())
					#print('YIELD TEXT', repr(token.match.group()))

				case actions if action is symbol.action.yield_match:
					result_stack[-1].append(token.match)
					#print('YIELD MATCH', repr(token.match))

				case actions if action is symbol.action.yield_token:
					result_stack[-1].append(token)
					#print('YIELD TOKEN', repr(token))

				case nothing if nothing is None:
					raise Exception(token.token, token.match)	#TODO - proper exception
					#print(token.token)

				case unhandled:
					raise Exception(action)

		return result_stack[-1]


class Enter_Sub_Parser(Structure):
	sub_parser = M.positional()

class Optional(Structure):
	value = M.positional()

class Expression(Structure):
	value = M.positional()

class Mnemonic(Structure):
	value = M.positional()


tp = Token_Parser('mnemonic', tokens=Tokens.mnemonic, post_processor=Mnemonic)

subp = Token_Parser('mnemonic-expression', tokens=Tokens.mnemonic_expression, post_processor=Expression)
subp.map_token_to_action(T.right_curly_bracket, symbol.action.exit_sub_parser)
subp.set_default_action(symbol.action.yield_text)

optp = Token_Parser('opt-expression', tokens=Tokens.opt_expression, post_processor=Optional)
optp.map_token_to_action(T.right_square_bracket, symbol.action.exit_sub_parser)
optp.set_default_action(symbol.action.yield_text)

tp.map_token_to_action(T.left_curly_bracket, Enter_Sub_Parser(subp))
tp.map_token_to_action(T.left_square_bracket, Enter_Sub_Parser(optp))
tp.set_default_action(symbol.action.yield_text)

test = 'title[:] {text}'
print(tp.process_text(test))

