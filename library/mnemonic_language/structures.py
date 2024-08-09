from ..record.base.public import Sequence, Structure
from ..record import member as M

class Optional(Sequence):
	pass

class Expression(Sequence):
	pass

class Mnemonic(Sequence):
	pass

#TODO - decide if we should use post_processor here or if that should be resovled with the Wrap_Capture features in the data conditions
#TODO - move to proper place in mnemonic_language
class mnemonic_argument(Structure):
	name = M.positional()
	#post_processor = M.positional(None)

	def acquire(self, processor_state):
		#if self.post_processor:
			#return self.post_processor(processor_state.captures[self.name])
		#else:
			#return processor_state.captures[self.name]

		return processor_state.captures[self.name]

class mnemonic_unwrapper(Structure):
	function = M.positional()
	arguments = M.positional(factory=list)

	def __call__(self, processor_state):
		return self.function(processor_state, *(arg.acquire(processor_state) for arg in self.arguments))


#TODO - we could potentially use the plain mnemonic_unwrapper if we make the argument setup flexible enough to include processor_state when we want
class mnemonic_unwrapper_for_records(Structure):
	record = M.positional()
	arguments = M.positional(factory=list)

	def __call__(self, processor_state):
		return self.record(*(arg.acquire(processor_state) for arg in self.arguments))



class pending_function_with_advanced_unwrapper(Structure):
	function = M.positional()
	mnemonic_implementation = M.positional()

	def get_arguments(self):
		return self.mnemonic_implementation.get_arguments()


	def __call__(self, function):
		return advanced_mnemonic_unwrapper(function, self.mnemonic_implementation)

class pending_argument(Structure):
	tag = M.positional()
	name = M.positional()

class argument_getter(Structure):
	function = M.positional()
	name = M.positional()

	def __call__(self):
		return self.function(self.name)

class advanced_mnemonic_unwrapper(Structure):
	function = M.positional()
	mnemonic_implementation = M.positional()

	def __call__(self, processor_state):
		positionals = list()
		for name, getter in self.mnemonic_implementation.compute_translation(self, processor_state).items():
			positionals.append(getter())

		return self.function(*positionals)


class pending_mnemonic_implementation(Structure):
	#processor_state = M.positional()
	context_setup = M.positional(factory=list)

	def copy(self):
		return pending_mnemonic_implementation(list(self.context_setup))

	def compute_translation(self, unwrapper, processor_state):
		#TODO - is this the right place to resolve this or should it be resolved when calling it? Could we have a different processor_state? Probably
		tag_lut = dict(
			PS = processor_state.__getattribute__,
			CTX = processor_state.context.require,
			MSYS = dict(processor_state=processor_state).__getitem__,
			CPT = processor_state.captures.__getitem__,
		)



		current_arguments = dict(
		 	processor_state = pending_argument('MSYS', 'processor_state'),
		)

		for mutation in unwrapper.mnemonic_implementation.context_setup:
			match mutation:
				case context_manipulation.include(name, alias, tag):
					current_arguments[alias or name] = pending_argument(tag, name)

				case context_manipulation.exclude(name, tag):
					assert tag == current_arguments.pop(name).tag	#TODO - figure out if we even need tag here

				case unhandled:
					raise Exception(unhandled)


		result = dict()	#Maybe this should be deferred to __call__ of unwrapper
		for (name, value) in current_arguments.items():
			result[name] = argument_getter(tag_lut[value.tag], value.name)	#TODO - this is a bit ugly, we should fix it

		return result




	def get_arguments(self):
		current_arguments = dict(
		 	processor_state = True,
		)

		for mutation in self.context_setup:
			match mutation:
				case context_manipulation.include(name, alias, tag):
					current_arguments[alias or name] = True

				case context_manipulation.exclude(name, tag):
					current_arguments.pop(name)

				case unhandled:
					raise Exception(unhandled)


		return current_arguments.keys()

class context_manipulation:
	class exclude(Structure):
		name = M.positional()
		tag = M.positional(None)

	class include(Structure):
		name = M.positional()
		alias = M.positional(None)
		tag = M.positional(None)
