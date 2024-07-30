from efforting.mvp6.record.base.public import Structure, Sequence
from efforting.mvp6.record import member as M
from efforting.mvp6.str.interface import String_Interface

from efforting.mvp6.processing import LUT_Processor, Type_LUT_Processor, Type_LUT_Comparator, Call_Comparator_Function

from efforting.mvp6.document import structures as DS

from efforting.mvp6 import symbol, ABC
T = symbol.text.token

from efforting.mvp6.iteration import branchable_iterator, Switchable_Iterator


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


v1 = DC.Sequence(word('define'), ws, optional(literal(':')), ws, DC.Capture_Remaining())

v2 = DC.Sequence(
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.word, match=DC.Structure_Match(match='define'))),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	(DC.Type_Instance(Optional) & DC.Sequence(
		(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.literal, match=DC.Structure_Match(match=':'))),
	)),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	DC.Capture_Remaining(),
)


print(v1 == v2)
print()


#v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], DC.Capture_Remaining(), require_sequence_type=Mnemonic)

v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], DC.Capture_Remaining('pattern'), require_sequence_type=Mnemonic)


print(v3)

test_tokens = tp.process_text('mnemonic function: define tree processor[:] {name}')
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

element_comparator = Type_LUT_Comparator('element_comparator')
sequence_comparator = Type_LUT_Comparator('sequence_comparator')
calculate_length = Type_LUT_Processor('calculate_length')




print('---')

@calculate_length.register(DC.Sequence)
def cl_sequence(processor, item):
	return sum(map(calculate_length.process_item, item))

@calculate_length.register(DC.All)
def cl_all(processor, item):
	return max(map(calculate_length.process_item, item))


@calculate_length.register(DC.Type_Instance)
@calculate_length.register(DC.Structure_Match)
def cl_one(processor, item):
	return 1



@element_comparator.register(DC.All)
def compare_all(comparator, expected, subject):
	for sub_item in expected:
		if comparator.compare_items(sub_item, subject) != expected.value:
			return False

	return True

@element_comparator.register(DC.Any)
def compare_any(comparator, expected, subject):
	for sub_item in expected:
		if comparator.compare_items(sub_item, subject) == expected.value:
			return True

	return False

@element_comparator.register(DC.Type_Instance)
def compare_type_instance(comparator, expected, subject):
	return isinstance(subject, expected.value)

@element_comparator.register(DC.Equality)
def compare_sequence(comparator, expected, subject):
	return expected.value == subject

@element_comparator.register(DC.Identity)
def compare_sequence(comparator, expected, subject):
	return expected.value is subject

@element_comparator.register(DC.Structure_Match)
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


@sequence_comparator.register(DC.Sequence)
def compare_sequence(comparator, expected, subject_iterator):

	#We may have stuff in a sequence that eats up all remaining items and so on
	#We should probably only allow for one of those so that we could have [..., A, B], [A, ..., B] and [A, B, ...]

	variable_index = None
	variable_capture = None
	for sub_index, sub_expected in enumerate(expected):
		if isinstance(sub_expected, DC.Capture_Remaining):
			assert variable_index is None	#Allow only one
			variable_capture = sub_expected
			variable_index = sub_index

	if variable_index is not None:
		head = expected[:variable_index]
		tail = expected[variable_index+1:]
	else:
		head = expected
		tail = None

	for expected_element in head:
		if not comparator.compare_items(expected_element, subject_iterator):
			return False

	if variable_index is not None:
		if tail:
			tl = calculate_length.process_item(tail)	#This might fail in case we don't know the exact elements remaining - which would make the pattern invalid
			#To put it better: A variable sized capture can not be followed by a variable size pattern (maybe we could do some sort of branching brute force later for this)

			subject_all_remaining = subject_iterator.drain()
			subject_tail = subject_all_remaining[-tl:]
			subject_remaining = subject_all_remaining[:-tl]		#NOTE - we may not need this for comparison but for capture it will be needed so we leave it here for now

			if variable_capture.name:
				comparator.store_capture(subject_remaining, variable_capture.name)

			tail_iterator = branchable_iterator(iter(subject_tail))

			for expected_element in tail:
				if not comparator.compare_items(expected_element, tail_iterator):
					return False
		else:
			if variable_capture.name:
				comparator.store_capture(subject_iterator.drain(), variable_capture.name)


	return True

@sequence_comparator.register_default()
def compare_sequence_default_element(comparator, expected, subject_iterator):
	value = next(subject_iterator)
	return element_comparator(comparator).compare_items(expected, value)


@element_comparator.register(type(DC.Always_True))
def compare_special(comparator, expected, subject):
	return True

@element_comparator.register(type(DC.Never_True))
def compare_special(comparator, expected, subject):
	return False

@element_comparator.register(DC.Sequence)
def compare_sequence_element(comparator, expected, subject):
	try:
		iterator = iter(subject)
	except TypeError:
		return False

	return sequence_comparator(comparator).compare_items(expected, branchable_iterator(iterator))



ec = element_comparator()


print(ec.compare_items(v3, test_tokens))
print(ec.captures['pattern'])

