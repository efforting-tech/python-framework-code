from ..processing.generic import Type_LUT_Processor, Type_LUT_Comparator
from ..matching import data_condition as DC
from ..iteration import branchable_iterator
from .. import symbol


#TODO - make sure we have overlapping coverage for the different comparators and processors here

element_comparator = Type_LUT_Comparator('element_comparator')
sequence_comparator = Type_LUT_Comparator('sequence_comparator')
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
	try:
		value = next(subject_iterator)
		return element_comparator(comparator).compare_items(expected, value)
	except StopIteration:
		return False


@element_comparator.register(type(DC.Always_True))
def compare_special(comparator, expected, subject):
	return True

@element_comparator.register(type(DC.Never_True))
def compare_special(comparator, expected, subject):
	return False

@element_comparator.register(DC.Update_Flag)
def compare_special(comparator, expected, subject):
	comparator.update_captured_flag(expected.capture, expected.flag, expected.value)
	return True

@element_comparator.register(DC.Wrap_Capture)
def compare_special(comparator, expected, subject):
	comparator.wrap_capture(expected.capture, expected.wrapper)
	return True

@element_comparator.register(DC.Call_Function)
def compare_special(comparator, expected, subject):

	positional = list()
	for p in expected.positional_captures:
		positional.append(comparator.captures[p])

	comparator.store_capture(expected.function(*positional), expected.target_capture)
	#comparator.wrap_capture(expected.capture, expected.wrapper)

	return True


@element_comparator.register(DC.Capture)
def compare_special(comparator, expected, subject):
	comparator.store_capture(subject, expected.name)
	return True

@element_comparator.register(DC.Set_Capture)
def compare_special(comparator, expected, subject):
	comparator.store_capture(expected.value, expected.capture)
	return True

@element_comparator.register(DC.Push_Capture)
def compare_special(comparator, expected, subject):
	if (target := comparator.get_capture(expected.capture)) is None:
		target = [subject]
		comparator.store_capture(target, expected.capture)
	else:
		target.append(subject)

	return True


#TODO - push/pop should support empty also, if you pop something that doesn't exist and then push that item (which should be a special symbol) it should delete the item in captures

@element_comparator.register(DC.Pop_And_Push_Capture)
def compare_special(comparator, expected, subject):
	comparator.captures[expected.target] = comparator.captures.pop(expected.source)
	return True

@element_comparator.register(DC.Push_Capture_State)
def compare_special(comparator, expected, subject):
	if (target := comparator.get_capture(expected.capture)) is None:
		target = [dict(comparator.captures)]
		comparator.store_capture(target, expected.capture)
	else:
		target.append(dict(comparator.captures))

	return True

@element_comparator.register(DC.Repeat)
def compare_special(comparator, expected, subject):
	#HACK - this is a brute force method for partial match, we should have a comparator specifically for this
	#		maybe we can put all our comparators in some sort of interface we can reuse (or in some named tree)

	#Check for some stuff we have not implemented yet
	assert expected.element_condition
	assert not expected.stop_condition
	assert expected.min_count is None
	assert expected.max_count is None

	remaining = subject

	while remaining:

		#from ..mnemonic_language.string_formatting_rules import string_formatter
		#print(f'checking {type(remaining).__qualname__}({string_formatter.process_item(remaining)!r})' )

		for l in range(len(remaining)):
			if l:
				brute_force_subject = remaining[:-l]
				pending_remaining = remaining[-l:]
			else:
				brute_force_subject = remaining[:]
				pending_remaining = None

			#print(f'BF {type(brute_force_subject).__qualname__}({string_formatter.process_item(brute_force_subject)!r})' )

			if comparator.compare_items(expected.element_condition, brute_force_subject):
				#print('Partial match for', repr(string_formatter.process_item(brute_force_subject)))
				remaining = pending_remaining
				break
		else:

			#print('No more find!')
			#print('remaining', string_formatter.process_item(remaining))

			#from efforting.mvp5.lazy_resources import acquire
			#acquire('terminal_dump')(expected.element_condition, skip_underscore=True)
			return False

	return True



@element_comparator.register(DC.Sequence)
def compare_sequence_element(comparator, expected, subject):
	try:
		iterator = iter(subject)
	except TypeError:
		return False

	bi = branchable_iterator(iterator)
	if sequence_comparator(comparator).compare_items(expected, bi) and bi.is_empty():
		return True
	else:
		return False