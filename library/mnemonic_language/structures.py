from ..record.base.public import Sequence, Structure
from ..record import member as M

class Optional(Sequence):
	pass

class Expression(Sequence):
	pass

class Mnemonic(Sequence):
	pass

#TODO - move to proper place in mnemonic_language
class mnemonic_argument(Structure):
	name = M.positional()
	post_processor = M.positional(None)

	def acquire(self, processor_state):
		if self.post_processor:
			return self.post_processor(processor_state.captures[self.name])
		else:
			return processor_state.captures[self.name]

class mnemonic_unwrapper(Structure):
	function = M.positional()
	arguments = M.positional(factory=list)

	def __call__(self, processor_state):
		return self.function(processor_state, *(arg.acquire(processor_state) for arg in self.arguments))
