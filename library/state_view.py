from .record.base.public import Structure, Mapping
from .record import member as M



class State_Mapping(Mapping):
	pass


class State_Interface(Structure):
	_state = M.positional(repr=False)
	_interface = M.positional(repr=False)
	#TODO - possibly support default values or some other way to handle unitialized states

	def __repr__(self):
		MISS = object()	#TODO local symbol
		values = ((n, self._state.get(s, MISS)) for n, s in self._interface.members.items())
		inner =  ', '.join(f'{n}={"N/A" if v is MISS else repr(v)}' for n, v in values)
		return f'{self.__class__.__qualname__}({inner})'

	def __getattr__(self, name):
		return self._state[self._interface.members[name]]

	def __setattr__(self, name, value):
		if name.startswith('_'):
			super().__setattr__(name, value)
		else:
			self._state[self._interface.members[name]] = value

	def __call__(self, item):
		match item:
			case State_Mapping() as state:
				return State_Interface(state, self._interface)

			case State_Interface(_state=state):
				return State_Interface(state, self._interface)

			case unhandled:
				raise Exception(unhandled)


class State_Interface_Definition(Structure):
	name = M.positional(None)
	members = M.all_named()

	def __call__(self, item):
		match item:
			case State_Mapping() as state:
				return State_Interface(state, self)

			case State_Interface(_state=state):
				return State_Interface(state, self)

			case unhandled:
				raise Exception(unhandled)

