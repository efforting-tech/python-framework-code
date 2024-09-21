from .. import Symbol
from . import record as R


class State_Manager_Transition_Interface(R.Record):
	_target: R.Field()
	_pending_transition: R.Field()

	def __call__(self):
		ts = self._pending_transition.to_state
		valid = self.is_valid()

		if self._target.assert_validity:
			assert valid, f'Can not transition from "{self._target.value}" to "{ts}".'

		if valid:
			self._target.value = ts

		return valid

	def is_valid(self):
		fs = self._pending_transition.from_states
		return (fs is Symbol.State_Management.Any_State) or self._target.value in fs

class State_Manager_Interface(R.Record):
	_target: R.Field()

	def __getattr__(self, name):
		return State_Manager_Transition_Interface(self._target, self._target.manager.transitions[name])

	def __dir__(self):
		return self._target.manager.transitions.keys()

class State(R.Record):
	manager: R.Field()
	value: R.Field()
	assert_validity: R.Field() = True

	@property
	def interface(self):
		return State_Manager_Interface(self)

	def __repr__(self):
		return f'State({self.value})'

class State_Manager(R.Record):
	states: R.Field()
	transitions: R.Field(factory=dict)
	default_state: R.Field()


	def __call__(self, value=None, assert_validity=True):
		if value is None:
			value = self.states[0]
		else:
			value = self.states[value]

		return State(self, value, assert_validity=assert_validity)


class Transition(R.Record):
	to_state: R.Field()
	from_states: R.Field() = Symbol.State_Management.Any_State


