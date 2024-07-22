

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
	def __init__(self, target_type):
		self.target_type = target_type

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
			if pending := getattr(ptr, piece, None):
				ptr = pending
			else:
				new = self.target_type(piece, ptr)
				if ptr._auto_graft is not None:
					ptr._auto_graft[new._name] = new

				setattr(ptr, piece, new)
				ptr = new

		return ptr

