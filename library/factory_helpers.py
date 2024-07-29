#TODO - move to other place
class Dict_As_Attributes:
	def __init__(self, target):
		self.__target = target

	def __getattr__(self, name):
		if name.startswith(f'_{type(self).__name__}'):
			return super().__getattr__(name)
		else:
			try:
				return self.__target[name]
			except KeyError as ke:
				raise AttributeError from ke 	#TODO - proper exception

	def __setattr__(self, name, value):
		if name.startswith(f'_{type(self).__name__}'):
			super().__setattr__(name, value)
		else:
			self.__target[name] = value

	def __delattr__(self, name):
		if name.startswith(f'_{type(self).__name__}'):
			super().__delattr__(name)
		else:
			try:
				del self.__target[name]
			except KeyError as ke:
				raise AttributeError from ke 	#TODO - proper exception






class Register_Interface:
	def __init__(self, target_type, data_wrapper=None, data_unwrapper=None):
		self.target_type = target_type
		self.data_wrapper = data_wrapper		#Not sure we will ever use these, maybe we could tidy them away unless a use case occurs (they were introduced duing a wild goose chase regarding the ABC system)
		self.data_unwrapper = data_unwrapper

	def register_entries_here(self, entries, stack_adjustment=0):
		self.register_entries_at_target(Dict_As_Attributes(sys._getframe(stack_adjustment + 1).f_locals), entries)

	def register_entries_at_target(self, target, entries):
		#TODO - support comments - we might have to have a local parser since tokenization/parsing features may depend on entries
		for entry in entries.split():
			self.register_entry(target, entry)

	def register_entry(self, target, entry):
		ptr = target

		parent = None
		for piece in entry.split('.'):
			assert not piece.startswith('_') #TODO - proper exception

			if self.data_unwrapper:
				unwrapped_ptr = self.data_unwrapper(ptr)
			else:
				unwrapped_ptr = ptr


			if pending := getattr(unwrapped_ptr, piece, None):
				ptr = pending
			else:
				new = self.target_type(piece, ptr)
				if ptr._auto_graft is not None:
					ptr._auto_graft[new._name] = new

				if self.data_wrapper:
					setattr(unwrapped_ptr, piece, self.data_wrapper(new))
				else:
					setattr(unwrapped_ptr, piece, new)
				ptr = new

		return ptr

