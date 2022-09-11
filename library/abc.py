from .data_directory import generic_data_directory
from .constants import UNDEFINED

_abc_directory = generic_data_directory()
_abc_registry = dict()

abc = _abc_directory.root_accessor

def create_abc(path):
	p = _abc_directory.cast_path(path)
	p_full = str(p)

	if p.parent.name and str(p.parent) not in _abc_directory:
		create_abc(p.parent)

	new_type = _abc_directory[p_full] = abc_type(p.name, (), dict(
		_path = p,
		_directory = _abc_directory,
	))

	return new_type

class abc_type(type):

	def __new__(cls, name, bases, scope):
		if bases:
			#assume we are creating a concrete class
			# - note here is where we would have machinery to create all kinds of custom classes
			new_type = type(name, (), scope)
			_abc_registry[new_type] = bases


			return new_type

		else:
			return type.__new__(cls, name, (), scope)

	def __getattr__(self, name):
		if not name.startswith('_'):
			if (candidate := self._directory[f'{self._path}.{name}']) is not UNDEFINED:
				return candidate

		raise AttributeError(f'{self} have no attribute {name!r}')

	def __repr__(self):
		#return type.__repr__(self)
		return f'_abc_directory[{str(self._path)!r}]'


	def __instancecheck__(cls, instance):
		bases = _abc_registry[instance.__class__]
		for candidate in cls._directory.get_directory(cls._path).walk():
			if _abc_directory[candidate.path] in bases:
				return True

		return False

	def __subclasscheck__(cls, subclass):
		bases = _abc_registry[subclass]
		for candidate in cls._directory.get_directory(cls._path).walk():
			if _abc_directory[candidate.path] in bases:
				return True

		return False


