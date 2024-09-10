from .record import member as M
from .record.base.public import Structure
from . import symbol

class Dict_As_Object_Read_Interface(Structure):
	_target = M.positional()
	_default = M.positional(symbol.action.raise_exception, repr=False)
	#TODO - later we may provide a dispatcher for wrapping values but here we will simply wrap dict

	def __dir__(self):
		return self._target.keys()


	def _resolve(self, value, key=None):

		match value:
			case dict():
				return type(self)(value, _default=self._default)
			case list() | tuple():
				return type(value)(map(self._resolve, value))

			case action if action is symbol.action.raise_exception:
				if key:
					raise AttributeError(f'{key!r} not in {self._target!r}')	#TODO - improve
				else:
					raise AttributeError(f'Failed to access value in {self._target!r}')	#TODO - improve
			case otherwise:
				return value

	def __getattr__(self, key):
		if key.startswith('_'):
			return super().__getattr__(key)
		else:
			return self._resolve(self._target.get(key, self._default), key)




def unpack_dict(target, *keys):
	yield from (target[k] for k in keys)

