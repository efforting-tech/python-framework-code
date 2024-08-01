from ..processing.generic import Type_LUT_Processor, Type_LUT_Comparator
from ..matching import data_condition as DC
from ..iteration import branchable_iterator
from .. import symbol


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
