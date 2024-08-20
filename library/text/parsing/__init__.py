from ...record.base.public import Structure
from ...record import member as M
from ...str.interface import String_Interface
from ... import symbol

from ...processing.dispatcher import Named_Dispatcher, LUT_Regulations, generic_data_condition, unconditional_rule
from ...matching import data_condition as DC

from .structures import Token_Stream, Enter_Sub_Parser


class Token_Rule(Structure):
	token = M.positional(None)
	value = M.positional(None)
	action = M.positional(True)

	def match(self, item):
		if self.token and self.token is not item.token:
			return

		if self.value is not None and self.value != item.value:
			return

		return True







class Token_Parser(Named_Dispatcher):
	regulations = M.positional(factory=LUT_Regulations)
	tokens = M.positional(factory=dict(), repr=False)
	post_processor = M.positional(tuple)

	def map_token_to_action(self, token, action):
		self.regulations.rules[token] = action

	def set_default_action(self, action):
		self.regulations.fallback_rule = unconditional_rule(action)



	def process_text(self, text, position=0):
		return self.process_token_stream(Token_Stream(None, text, position))

	def process_token_stream(self, token_stream):
		return self.post_processor(tuple(self.process_token_stream_iteratively(token_stream)))

	def process_token_stream_iteratively(self, token_stream):
		token_stream.source = String_Interface.regex_tokenize(token_stream.text, self.tokens, token_stream.pending_position)
		for token in token_stream:

			action = self.dispatch_item(token.token).value.rule.action
			#print('TOKEN', self.name, token.token, repr(token.match.group()), action)

			match action:
				case Enter_Sub_Parser(target):
					#print('ENTER', target.name)
					token_stream.pending_position = token.match.end()
					yield target.process_token_stream(token_stream)
					token_stream.source = String_Interface.regex_tokenize(token_stream.text, self.tokens, token_stream.pending_position)

				case actions if action is symbol.action.exit_sub_parser:
					#print('EXIT', self.name)
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

