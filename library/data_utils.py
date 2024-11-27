from .record import member as M
from .record.base.public import Structure
from . import Symbol

class Dict_As_Object_Read_Interface(Structure):
	_target = M.positional()
	_default = M.positional(Symbol.Action.Raise_Exception, repr=False)
	#TODO - later we may provide a dispatcher for wrapping values but here we will simply wrap dict

	def __dir__(self):
		return self._target.keys()


	def _resolve(self, value, key=None):

		match value:
			case dict():
				return type(self)(value, _default=self._default)
			case list() | tuple():
				return type(value)(map(self._resolve, value))

			case action if action is Symbol.Action.Raise_Exception:
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


def list_from_lines_with_content(text, strip=True):
	if strip:
		return list(filter(bool, map(str.strip, text.splitlines())))
	else:
		return list(filter(bool, text.splitlines()))


def flatten(item):
	match item:
		case list() | map():
			result = list()
			for sub_item in item:
				result.extend(flatten_if_present(sub_item))

			return result

		case otherwise:
			return [otherwise]

def flatten_if_present(item):
	return list(filter(bool, flatten(item)))


def csloi(text): #Comma separated list of identifiers
	return tuple(filter(bool, map(str.strip, text.split(','))))
