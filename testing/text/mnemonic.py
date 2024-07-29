from efforting.mvp6.record.base.public import Structure, Sequence
from efforting.mvp6.record import member as M
from efforting.mvp6.str.interface import String_Interface

from efforting.mvp6.processing import LUT_Processor, Type_LUT_Comparator, Call_Comparator_Function

from efforting.mvp6.document import structures as DS

from efforting.mvp6 import symbol, ABC
T = symbol.text.token


# print(type(LUT_Processor))
# print()



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


@ABC.Action
class Enter_Sub_Parser(Structure):
	sub_parser = M.positional()


class Optional(Sequence):
	pass

class Expression(Sequence):
	pass

class Mnemonic(Sequence):
	pass


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
	#return DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(token), match=DC.Structure_Match(match=value))
	return DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(token), match=DC.Structure_Match(group=DC.Call_And_Compare_Return_Value(value)))

def word(value):
	return literal_token(T.word, DC.Equality(value))

def literal(value):
	return literal_token(T.literal, DC.Equality(value))

def optional(*sub_items):
	return DC.Sequence(*sub_items) | DC.Always_True

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


#v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], symbol.remaining_elements, require_sequence_type=Mnemonic)

v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], symbol.remaining_elements, word('yo'), require_sequence_type=Mnemonic)


print(v3)

test_tokens = tp.process_text('mnemonic function: define tree processor: {name} yo')
print()
print(test_tokens)

print()
from efforting.mvp5.lazy_resources import acquire
import os
os.system('tabs 4')
dump = acquire('terminal_dump')


#TODO - custom data dumping!
#dump(v3, skip_underscore=True)

#for t in test_tokens:
#	print(t)



#When we compare this, we may want a rule system since we may want to do very different things in different circumstances

#Next up - compare test_tokens with v3 using a comparing processor

comparator = Type_LUT_Comparator()

print('---')

@comparator.register(DC.All)
def compare_all(comparator, expected, subject):
	for sub_item in expected:
		if not comparator.compare_items(sub_item, subject):
			return False

	return True

@comparator.register(DC.Any)
def compare_any(comparator, expected, subject):
	for sub_item in expected:
		if comparator.compare_items(sub_item, subject):
			return True

	return False

@comparator.register(DC.Type_Instance)
def compare_type_instance(comparator, expected, subject):
	return isinstance(subject, expected.value)

@comparator.register(DC.Equality)
def compare_sequence(comparator, expected, subject):
	return expected.value == subject

@comparator.register(DC.Identity)
def compare_sequence(comparator, expected, subject):
	return expected.value is subject

@comparator.register(DC.Structure_Match)
def compare_sequence(comparator, expected, subject):
	for name, sub_expected in expected.value.items():
		if isinstance(sub_expected, DC.Call_And_Compare_Return_Value):
			if method := getattr(subject, name, None):
				if not comparator.compare_items(sub_expected.value, method()):
					return False
			else:
				return False
		else:
			sub_value = getattr(subject, name, symbol.miss)	#We use a global miss here so we can test for it if we want that
			if not comparator.compare_items(sub_expected, sub_value):
				return False

	return True

@comparator.register(DC.Sequence)
def compare_sequence(comparator, expected, subject):
	#TODO - we must utilize the branchable iterator here.
	#		but this means we should expect our subject to be the branchable iterator
	#		if it is not we must put it in one
	#		The question then becomes if comparator should have a different API for dealing with the BI

	#Here we get to a tricky proposition

	#We may have stuff in a sequence that eats up all remaining items and so on
	#We should probably only allow for one of those so that we could have [..., A, B], [A, ..., B] and [A, B, ...]

	variable_index = None
	for sub_index, sub_expected in enumerate(expected):
		if sub_expected is symbol.remaining_elements:
			assert variable_index is None	#Allow only one
			variable_index = sub_index

	if variable_index is not None:
		head = expected[:variable_index]
		tail = expected[variable_index+1:]
	else:
		head = expected
		tail = None



	#BUG - We solved the eat-all problem, but we haven't solved optional branches
	for i, sub_expected in enumerate(head):
		print(i, sub_expected, comparator.compare_items(sub_expected, subject[i]))


#comparator.rules.map_action(DC.All, Call_Comparator_Function(compare_all))


# #SIDE NOTE
# import re

# match re.compile('.*').match('hello world'):
# 	case re.Match(group=g) if g() == 'hello world':
# 		print('Wee')

# exit()

comparator.compare_items(v3, test_tokens)
