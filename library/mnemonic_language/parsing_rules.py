from ..processing.generic import Type_LUT_Processor, Type_LUT_Comparator
from ..matching import data_condition as DC
from ..iteration import branchable_iterator
from .. import symbol, ABC



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





mnemonic_comparator = Type_LUT_Comparator('mnemonic_comparator')	#Operates on branchable_iterator

def compare_mnemonic_items(expected, subject, processor_state=None):
	if isinstance(processor_state, ABC.Processor_State):
		return processor_state.with_processor(mnemonic_comparator).compare_items(expected, branchable_iterator((subject,)))
	else:
		return mnemonic_comparator.compare_items(expected, branchable_iterator((subject,)))

@mnemonic_comparator.register(DC.All)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	for sub_item in expected:
		if not comparator.compare_items(sub_item, subject_iterator.branch()):
			return False

	subject_iterator.pop()
	return True

@mnemonic_comparator.register(DC.Type_Instance)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	if (pending := subject_iterator.pop(MISS)) is not MISS:
		#print('TI', expected, pending)
		return isinstance(pending, expected.value)
	else:
		return False

@mnemonic_comparator.register(DC.Identity)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	#print('ID', expected, subject_iterator.peek('N/A'))
	return expected.value is subject_iterator.pop(MISS)

@mnemonic_comparator.register(DC.Equality)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	#print('EQ', expected, subject_iterator.peek('N/A'))
	return expected.value == subject_iterator.pop(MISS)

@mnemonic_comparator.register(DC.Capture_Remaining)
def compare_items(comparator, expected, subject_iterator):
	remaining = subject_iterator.drain()
	#print('CAPT_R', expected, remaining)
	comparator.store_capture(remaining, expected.name)	#NOTE - This requires comparator to be stateful
	return True

@mnemonic_comparator.register(DC.Wrap_Capture)
def compare_items(comparator, expected, subject_iterator):
	#print('CAPT_WRAP', expected)
	comparator.wrap_capture(expected.capture, expected.wrapper)	#NOTE - This requires comparator to be stateful
	return True

@mnemonic_comparator.register(DC.Capture)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	if (pending := subject_iterator.pop(MISS)) is not MISS:
		#print('CAPT', expected, pending)
		comparator.store_capture(pending, expected.name)	#NOTE - This requires comparator to be stateful
		return True
	else:
		return False

@mnemonic_comparator.register(DC.Sequence)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol


	#TODO - we must have a look ahead that spans all sub levels from the top level (we could use the processor_state for this, possibly we need a specific processor_state that have the proper members we require for state handling).
	#		Silicon Ducking: https://chatgpt.com/share/21b6f27f-7c32-49f4-814a-71d0caf4a08c

	if (pending := subject_iterator.pop(MISS)) is not MISS:
		sequence_iterator = branchable_iterator(pending)
		for sub_expected in expected:
			print('SEQUENCE', sub_expected, sequence_iterator.peek('N/A'))
			if not comparator.compare_items(sub_expected, sequence_iterator):
				print('FAIL')
				return False

		return True
	else:
		return False

@mnemonic_comparator.register(DC.Structure_Match)
def compare_items(comparator, expected, subject_iterator):
	MISS = object()	#TODO - local symbol
	if (pending := subject_iterator.pop(MISS)) is not MISS:
		for name, sub_expected in expected.value.items():
			#TODO - this should probably be its own resolver
			if isinstance(sub_expected, DC.Call_And_Compare_Return_Value):
				if method := getattr(pending, name, None):
					if not compare_mnemonic_items(sub_expected.value, method(), comparator):
						return False
				else:
					return False
			else:
				sub_value = getattr(pending, name, symbol.miss)	#We use a global miss here so we can test for it if we want that
				#print('STRUCTURE', name, sub_expected, sub_value)
				if not compare_mnemonic_items(sub_expected, sub_value, comparator):
					return False

		return True


	else:
		return False
