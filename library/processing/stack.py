from ..record import member as M
from ..record.base.public import Structure, Sequence
from .. import ABC, symbol

#TODO - move this to data utils
def consequtive_sub_sequence_sampling(source, length, strict=True):
	iterator = iter(source)
	while True:
		sub_sequence = list()
		for i in range(length):
			try:
				sub_sequence.append(next(iterator))
			except StopIteration:
				break

		if not sub_sequence:
			return
		elif len(sub_sequence) == length:
			yield sub_sequence
		elif strict:
			raise Exception('uneven sequence sub sampling')	#TODO improve message
		else:
			return


#TODO possibly move this outside of processing

class Stack(Sequence):
	push = Sequence.append

	def __bool__(self):
		return True

	@property
	def is_empty(self):
		return len(self) == 0

	@property
	def value(self):
		if len(self):
			return self[-1]
		else:
			return symbol.empty		#NOTE: If we were to return symbol.no_value we get an exception due to data descriptor failure
			#TODO - this and similar notes should be compiled into the documentation so that we can warn about it in the relevant places - possibly also have a section of recommended code models

	def pop(self, default=symbol.action.raise_exception):
		if len(self):
			return super().pop(-1)
		elif default is symbol.action.raise_exception:
			raise Exception('pop from empty stack')	#TODO improve message
		else:
			return default



class Stack_Frame(Structure):
	updates = M.all_positional()	#A list of alternating target stacks and values (var1, value1, var2, value2) where var supports the push/pop protocol

	def __enter__(self):
		for target, value in consequtive_sub_sequence_sampling(self.updates, 2):
			target.push(value)

	def __exit__(self, et, ev, tb):
		for target, value in consequtive_sub_sequence_sampling(self.updates, 2):
			target.pop()
