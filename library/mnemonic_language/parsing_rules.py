from .. import symbol, ABC
from ..iteration import branchable_iterator
from ..matching import data_condition as DC
from ..processing.generic import Type_LUT_Processor, Type_LUT_Comparator
from ..processing.structures import Call_Comparator_Function

#PENDING

# compare_items( [Sequence(= 123, Repeat() & (as stuff), = 456, = 789)] :: [[123, 1, 2, 3, 456, 789]]) ...
# compare_items( [= 123, Repeat() & (as stuff), = 456, = 789] :: [123, 1, 2, 3, 456, 789]) ...
# LUT_Rule(value=<Equality>, action=Call_Comparator_Function(function=𝑓<compare_items>)) → True
# compare_items( [Repeat() & (as stuff), = 456, = 789] :: [1, 2, 3, 456, 789]) ...

	# When we enter repeat we lose [ = 456, = 789] and therefore we have no implied lookahead - it must span levels!

# compare_items( [Repeat()] :: [1, 2, 3, 456, 789]) ...
# Element condition: None
# Stop condition: None
# Implied look ahead condition: ()




#NEXT UP: Figure out why our matching doesn't properly work ('stuff as thing' in bootstrap)

#REQUIREMENT: comparison functions must advance iterator upon matching and must not do it otherwise



#TODO - make sure we have overlapping coverage for the different comparators and processors here


calculate_length = Type_LUT_Processor('calculate_length')

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

@calculate_length.register(DC.Capture)
@calculate_length.register(DC.Wrap_Capture)
def cl_zero(processor, item):
	return 0



# prepare_pattern = Type_LUT_Processor('prepare_pattern')

# @prepare_pattern.register(DC.All)
# def pp(processor, item):
# 	for sub_item in item:
# 		processor.process_item(sub_item)

# @prepare_pattern.register(DC.Sequence)
# def pp(processor, item):
# 	previous = None
# 	for sub_item in item:
# 		if previous:

# 			from ..mnemonic_language.data_condition_formatting import dc_formatter
# 			print(f'{dc_formatter.process_item(previous)!r} → {dc_formatter.process_item(sub_item)!r}')

# 		processor.process_item(sub_item)
# 		previous = sub_item

# @prepare_pattern.register(DC.Structure_Match)
# def pp(processor, item):
# 	for name, sub_expected in item.value.items():
# 		processor.process_item(sub_expected)


# @prepare_pattern.register(DC.Call_And_Compare_Return_Value)
# @prepare_pattern.register(DC.Type_Instance)
# @prepare_pattern.register(DC.Identity)
# @prepare_pattern.register(DC.Equality)
# @prepare_pattern.register(DC.Capture)
# @prepare_pattern.register(DC.Capture_Remaining)
# @prepare_pattern.register(DC.Wrap_Capture)
# def pp(processor, item):
# 	pass





# mnemonic_comparator = Type_LUT_Comparator('mnemonic_comparator')	#Operates on branchable_iterator

# def compare_mnemonic_items(expected, subject, processor_state=None):
# 	#prepare_pattern.process_item(expected)	#TODO - should we do it here?
# 	if isinstance(processor_state, ABC.Processor_State):
# 		p = processor_state.with_processor(mnemonic_comparator)
# 		return p.compare_items(expected, branchable_iterator((subject,)))
# 	else:
# 		return mnemonic_comparator.compare_items(expected, branchable_iterator((subject,)))






class Mnemonic_Comparator(Type_LUT_Comparator):
	#This comparator expects both subject and expected to be branchable_iterators
	def compare_items(self, expected, subject):
		MISS = object()	#TODO local symbol


		if not isinstance(expected, branchable_iterator):
			expected = branchable_iterator((expected,))

		if not isinstance(subject, branchable_iterator):
			subject = branchable_iterator((subject,))


		from .data_condition_formatting import dc_formatter
		debug_info = f'compare_items( {dc_formatter.process_item(expected.branch().drain())} :: {dc_formatter.process_item(subject.branch().drain())})'
		print(f'{debug_info} ...')

		if (expected_element := expected.peek(MISS)) is MISS:
			print(f'{debug_info} → No element')
			return False

		subject_element = subject.peek(symbol.end_of_pattern)
		debug_cond = self.rules.lookup_rule(type(expected_element))

		match self.rules.lookup_action(type(expected_element)):
			case Call_Comparator_Function(function):
				result = function(self, expected, subject)
				print(f'{debug_cond} → {result}')
				return result

			case sym if sym is symbol.action.raise_exception:
				raise Exception(f'Failed to compare {subject_element!r} to {expected_element} in {type(self).__qualname__} {self.name!r}')

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case sym if sym in symbol.action:
				raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {unhandled}')	#TODO - better error

		print(f'{debug_cond} → False')
		return False


mnemonic_comparator = Mnemonic_Comparator('mnemonic_comparator')



@mnemonic_comparator.register(DC.All)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol
	subject_iterator_branch = None
	for sub_expectation in expected_iterator.peek((symbol.end_of_pattern,)):
		if sub_expectation is symbol.end_of_pattern:
			break		#TODO - figure out how we should deal with partial matches. Should we have a special matcher for full match? Or a configuration bit?

		subject_iterator_branch = subject_iterator.branch()
		#TODO - make sure all subject_iterator_branch are either not advanced or advanced the same amount
		if not comparator.compare_items(sub_expectation, subject_iterator_branch):
			print('sub fail', sub_expectation, subject_iterator_branch)
			return False

	if subject_iterator_branch:
		subject_iterator.synchronize_with(subject_iterator_branch)

	expected_iterator.pop()
	return True


@mnemonic_comparator.register(DC.Type_Instance)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol

	if (expected := expected_iterator.peek(MISS)) is MISS:
		return False

	if (subject := subject_iterator.peek(MISS)) is MISS:
		return False

	subject_iterator.pop()
	expected_iterator.pop()

	return isinstance(subject, expected.value)


@mnemonic_comparator.register(DC.Identity)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol

	if (expected := expected_iterator.peek(MISS)) is MISS:
		return False

	if (subject := subject_iterator.peek(MISS)) is MISS:
		return False

	subject_iterator.pop()
	expected_iterator.pop()

	return subject is expected.value



@mnemonic_comparator.register(DC.Equality)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol

	if (expected := expected_iterator.peek(MISS)) is MISS:
		return False

	if (subject := subject_iterator.peek(MISS)) is MISS:
		return False

	subject_iterator.pop()
	expected_iterator.pop()

	return subject == expected.value


@mnemonic_comparator.register(DC.Sequence)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol

	if (expected := expected_iterator.peek(MISS)) is MISS:
		return False

	if (subject := subject_iterator.peek(MISS)) is MISS:
		return False

	try:
		sequence_iterator = branchable_iterator(subject)
	except TypeError:	#TODO - check if iterable
		return False

	#for sub_expected in expected:
		#if not comparator.compare_items(sub_expected, sequence_iterator):
		#	return False


	sub_expection_iterator = branchable_iterator(expected)
	#print('SEI', sub_expection_iterator.branch().drain())
	for v in range(10):	#TODO
		if not comparator.compare_items(sub_expection_iterator, sequence_iterator):
			print('Terminate')
			return False




	subject_iterator.pop()
	expected_iterator.pop()

	return True

@mnemonic_comparator.register(DC.Structure_Match)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol

	if (expected := expected_iterator.peek(MISS)) is MISS:
		return False

	if (subject := subject_iterator.peek(MISS)) is MISS:
		return False

	for name, sub_expected in expected.value.items():
		#TODO - this should probably be its own resolver
		if isinstance(sub_expected, DC.Call_And_Compare_Return_Value):
			if method := getattr(subject, name, None):
				if not comparator.compare_items(sub_expected.value, method()):
					return False
			else:
				return False
		else:
			sub_value = getattr(subject, name, symbol.miss)	#We use a global miss here so we can test for it if we want that
			#print('STRUCTURE', name, sub_expected, sub_value)
			if not comparator.compare_items(sub_expected, sub_value):
				return False


	subject_iterator.pop()
	expected_iterator.pop()

	return True



# @mnemonic_comparator.register(DC.Capture_Remaining)
# def compare_items(comparator, expected_iterator, subject_iterator):
# 	remaining = subject_iterator.drain()
# 	expected = expected_iterator.pop()

# 	print('Remaining:', remaining)
# 	print('Look ahead condition:', expected_iterator.branch().drain())


# 	comparator.store_capture(remaining, expected.name)	#NOTE - This requires comparator to be stateful
# 	return True

@mnemonic_comparator.register(DC.Repeat)
def compare_items(comparator, expected_iterator, subject_iterator):
	expected = expected_iterator.pop()


	print('Element condition:', expected.element_condition)
	print('Stop condition:', expected.look_ahead_stop_condition)
	print('Implied look ahead condition:', expected_iterator.branch().drain())

	exit()

	comparator.store_capture(remaining, expected.name)	#NOTE - This requires comparator to be stateful
	return True

@mnemonic_comparator.register(DC.Wrap_Capture)
def compare_items(comparator, expected_iterator, subject_iterator):
	expected = expected_iterator.pop()
	comparator.wrap_capture(expected.capture, expected.wrapper)	#NOTE - This requires comparator to be stateful
	return True

@mnemonic_comparator.register(DC.Capture)
def compare_items(comparator, expected_iterator, subject_iterator):
	MISS = object()	#TODO - local symbol
	subject = subject_iterator.pop()
	expected = expected_iterator.pop()
	comparator.store_capture(subject, expected.name)	#NOTE - This requires comparator to be stateful
	return True
