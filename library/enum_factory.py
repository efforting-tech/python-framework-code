from .symbol_factory import Symbol

class Enum(Symbol):
	_REPR_PREFIX = 'E'
	def __dir__(self):
		path_start = len(self._path) + 1
		return [s._path[path_start:] for s in self._iter_children(True, True)]

	def __getitem__(self, key):
		if isinstance(key, Symbol):	#TODOC - this is because we may want to filter strings/enum entries
			return key

		elif isinstance(key, int):
			path_start = len(self._path) + 1
			return getattr(self, [s._path[path_start:] for s in self._iter_children(True, True)][key])

		else:
			ptr = self
			for piece in key.split('.'):
				ptr = getattr(ptr, piece)

			assert tuple(ptr._iter_children()) == ()	#TODO -proper exception
			return ptr



def convert_symbol_to_enum(symbol):
	symbol.__class__ = Enum

