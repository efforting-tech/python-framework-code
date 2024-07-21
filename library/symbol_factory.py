import sys

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



class Symbol:
	def __init__(self, name, parent=None, auto_graft=None):
		self._name = name
		self._parent = parent
		self._auto_graft = auto_graft

	def _set_auto_graft_here(self, stack_adjustment=0):
		self._auto_graft = sys._getframe(stack_adjustment + 1).f_locals

	def _iter_children(self, recursive=False, leaf_only=False):
		for name in object.__dir__(self):
			if name.startswith('_'):
				continue

			child = getattr(self, name)

			if recursive:
				if not leaf_only or (leaf_only and not(tuple(child._iter_children()))):
					yield child

				yield from child._iter_children(recursive, leaf_only)

			else:
				yield child




	@property
	def _path(self):
		if self._parent:
			return f'{self._parent._path}.{self._name}'
		else:
			return self._name

	def __repr__(self):
		return f'{type(self).__name__}({self._path!r})'

def register_symbols_here(symbols, stack_adjustment=0):
	register_symbols_at_target(Dict_As_Attributes(sys._getframe(stack_adjustment + 1).f_locals), symbols)

def register_symbols_at_target(target, symbols):
	#TODO - support comments - we might have to have a local parser since tokenization/parsing features may depend on symbols
	for entry in symbols.split():
		register_symbol(target, entry)

def register_symbol(target, symbol):
	ptr = target
	parent = None
	for piece in symbol.split('.'):
		assert not piece.startswith('_') #TODO - proper exception
		if pending := getattr(ptr, piece, None):
			ptr = pending
		else:
			new = Symbol(piece, ptr)
			if ptr._auto_graft is not None:
				ptr._auto_graft[new._name] = new

			setattr(ptr, piece, new)
			ptr = new

	return ptr

