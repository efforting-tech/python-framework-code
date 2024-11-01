#TODO - move to proper place

from efforting.mvp6.core import record as R
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.str.interface import String_Interface
from efforting.mvp6.iteration import Switchable_Iterator
from efforting.mvp6.core.data import Stack

import re

#TODO - move to efforting.mvp6.core.text.tokenization
class Tokenization_Result(R.Record):
	text: R.Field()
	start: R.Field()
	tokens: R.Field(factory=list)
	end: R.Field() = None
	finalized: R.Field() = False

	def __iter__(self):
		yield from self.tokens

	def emit(self, item):
		self.tokens.append(item)





#These are records for the things our tokenizer may encounter
class Inline(R.Record):
	value: R.Field()

class Text(R.Record):
	value: R.Field()

#This is a specification for a tokenizer
main = Tokenization_Specifier('main')
inline = Tokenization_Specifier('inline')

main.register_literal_token('«', A.Enter_Tokenizer(inline))
main.register_literal_token('»', A.Raise_Exception)
main.register_default(A.Emit(A.Wrap(Text)))

inline.register_literal_token('»', A.Return)
inline.register_default(A.Emit(A.Wrap(Inline)))



def create_tokenizer():
	main_tokens = re.compile('«'), re.compile('»'), None
	inline_tokens = main_tokens[1], None

	def tokenize(text, start=0, strict=True):
		result = Tokenization_Result()
		stack = Stack()
		action_handler = None

		def main_actions(token):
			nonlocal action_handler

			tid = token.token
			if tid == 0:
				stack.push((action_handler, main_tokens))
				token_stream.source = String_Interface.regex_tokenize(text, inline_tokens, token.match.end())
				action_handler = inline_actions

			elif tid == 1:
				raise Exception(f'Unexpected {token} in tokenizer "main".')

			elif tid == 2:
				result.emit(Text(token.match.group()))

			else:
				raise Exception()


		def inline_actions(token):
			nonlocal action_handler

			tid = token.token
			if tid == 0:
				(action_handler, tokens) = stack.pop()
				token_stream.source = String_Interface.regex_tokenize(text, tokens, token.match.end())

			elif tid == 1:
				result.emit(Inline(token.match.group()))

			else:
				raise Exception()

		token_stream = Switchable_Iterator(String_Interface.regex_tokenize(text, main_tokens, start))
		action_handler = main_actions

		for token in token_stream:
			action_handler(token)
			result.end = token.match.end()

		result.finalized = len(stack) == 0
		if strict and not result.finalized:
			raise Exception()

		return result

	return tokenize


tokenizer = create_tokenizer()

result = tokenizer('hello «world»!')
print(result.end, result.finalized)
for token in result:
	print(token)
