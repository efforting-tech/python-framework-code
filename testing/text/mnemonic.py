
from efforting.mvp6.processing import LUT_Processor


print(LUT_Processor)

assert not 'Member' in dir(LUT_Processor)
assert not LUT_Processor.Member


exit()

class ABC_Meta_Value:
	def __init__(self, value):
		self.value = value

	def __get__(self, instance, owner):
		if instance is not None:
			raise AttributeError()

		return self.value

class ABC_Meta(type):
	stuff = ABC_Meta_Value('stuff')


class ABC_Meta_Sub(ABC_Meta):
	tree = ABC_Meta_Value('hello')

class ABC_Node(metaclass=ABC_Meta):
	pass


class ABC_Sub_Node(metaclass=ABC_Meta_Sub):
	pass

print(type(ABC_Sub_Node).tree)


assert hasattr(ABC_Meta, 'stuff')
assert not hasattr(ABC_Node, 'stuff')
assert 'stuff' in dir(ABC_Meta)
assert 'stuff' not in dir(ABC_Node)

exit()


print(object().mro)

from efforting.mvp6.record.base.public import Structure, Sequence
from efforting.mvp6.record import member as M
from efforting.mvp6.str.interface import String_Interface

from efforting.mvp6.processing import LUT_Processor

from efforting.mvp6.document import structures as DS

from efforting.mvp6 import symbol
T = symbol.text.token


print(type(LUT_Processor))
print()


class new_class:
	stuff = 123

assert new_class.stuff == new_class().stuff

print(LUT_Processor())
exit()

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
	tokens = M.positional(factory=dict(), repr=False)
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
			#print(self.name, token.token, action)

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

class Optional(Sequence):
	value = M.positional()

class Expression(Sequence):
	value = M.positional()

class Mnemonic(Sequence):
	value = M.positional()


tp = Token_Parser('mnemonic', tokens=Tokens.mnemonic, post_processor=lambda p: Mnemonic(*p))

subp = Token_Parser('mnemonic-expression', tokens=Tokens.mnemonic_expression, post_processor=lambda p: Expression(*p))
subp.map_token_to_action(T.right_curly_bracket, symbol.action.exit_sub_parser)
subp.set_default_action(symbol.action.yield_token)

optp = Token_Parser('opt-expression', tokens=Tokens.opt_expression, post_processor=lambda p: Optional(*p))
optp.map_token_to_action(T.right_square_bracket, symbol.action.exit_sub_parser)
optp.set_default_action(symbol.action.yield_token)

tp.map_token_to_action(T.left_curly_bracket, Enter_Sub_Parser(subp))
tp.map_token_to_action(T.left_square_bracket, Enter_Sub_Parser(optp))
tp.set_default_action(symbol.action.yield_token)

test = 'title[:] {text}'
print(tp.process_text(test))
print()

from efforting.mvp6.matching import data_condition as DC


#Helpers
def literal_token(token, value):
	return DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(token), match=DC.Structure_Match(match=value))

def word(value):
	return literal_token(T.word, value)

def literal(value):
	return literal_token(T.literal, value)

def optional(*sub_items):
	return DC.Type_Instance(Optional) & DC.Sequence(*sub_items)

def join_sequence(separator, *sequence, expand_sub_sequences=True, require_sequence_type=None):
	#NOTE  that expand_sub_sequences does not insert separators, which is the idea of it.
	#		to do it differently, just call this function with an already expanded sequence
	NO_ITEM = object()	#TODO - local symbol
	last_item = NO_ITEM
	result = DC.Sequence()
	for item in sequence:
		if last_item is not NO_ITEM:
			result.append(separator)

		if expand_sub_sequences and type(item) in (tuple, list):	#Note that we require pure tuple or list, not descendents
			result.extend(item)
		else:
			result.append(item)
		last_item = item

	if require_sequence_type:
		return DC.Type_Instance(require_sequence_type) & result
	else:
		return result

ws = DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(T.whitespace))

#End of helpers




v1 = DC.Sequence(word('define'), ws, optional(literal(':')),	ws, symbol.remaining_elements)

v2 = DC.Sequence(
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.word, match=DC.Structure_Match(match='define'))),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	(DC.Type_Instance(Optional) & DC.Sequence(
		(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.literal, match=DC.Structure_Match(match=':'))),
	)),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	symbol.remaining_elements,
)


print(v1 == v2)
print()


v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], symbol.remaining_elements, require_sequence_type=Mnemonic)

print(v3)

test_tokens = tp.process_text('mnemonic function: define tree processor: {name}')
print()
print(test_tokens)

print()
from efforting.mvp5.lazy_resources import acquire
import os
os.system('tabs 4')
dump = acquire('terminal_dump')


#TODO - custom data dumping!


dump(v3, skip_underscore=True, skip_not_assigned=True)


#When we compare this, we may want a rule system since we may want to do very different things in different circumstances