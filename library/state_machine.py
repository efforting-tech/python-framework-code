from . import symbol
from .record.base.public import Structure
from .record import member as M


class State_Manager_Transition_Interface(Structure):
	_target = M.positional()
	_pending_transition = M.positional()

	def __call__(self):
		ts = self._pending_transition.to_state
		valid = self.is_valid()

		if self._target.assert_validity:
			assert valid, f'Can not transition from "{self._target.value._name}" to "{ts._name}".'

		if valid:
			self._target.value = ts

		return valid

	def is_valid(self):
		fs = self._pending_transition.from_states
		return (fs is symbol.state_management.any_state) or self._target.value in fs

class State_Manager_Interface(Structure):
	_target = M.positional()

	def __getattr__(self, name):
		return State_Manager_Transition_Interface(self._target, self._target.manager.transitions[name])

	def __dir__(self):
		return self._target.manager.transitions.keys()

class State(Structure):
	manager = M.positional()
	value = M.positional()
	assert_validity = M.positional(True)

	@property
	def interface(self):
		return State_Manager_Interface(self)

	def __repr__(self):
		return f'State({self.value._name})'

class State_Manager(Structure):
	states = M.positional()
	transitions = M.positional(factory=dict)
	default_state = M.positional()


	def __call__(self, value=None, assert_validity=True):
		if value is None:
			value = self.states[0]
		else:
			value = self.states[value]

		return State(self, value, assert_validity=assert_validity)


class Transition(Structure):
	to_state = M.positional()
	from_states = M.positional(symbol.state_management.any_state)


