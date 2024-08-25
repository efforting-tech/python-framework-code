from . import symbol
from .record import member as M
from .record.base.public import Structure
from .state_machine import State_Manager, Transition
import random


S = symbol.aggregator.status

class Aggregator(Structure):
	state_manager = State_Manager(S, dict(
		abort = Transition(S.Aborted, {S.Pending, S.Working}),
		finish = Transition(S.Finished, {S.Pending, S.Working}),
		work = Transition(S.Working, {S.Pending, S.Working}),
		reset = Transition(S.Pending),
	))

	_state = M.positional(factory=state_manager, repr=False)
	error = M.positional(None)

	#TODO - we should have a way to include properties in the representation
	@property
	def state(self):
		return self._state.value

	@property
	def accepting_work(self):
		return self._state.interface.work.is_valid()

	#NOTE - later we may want to use some decorator for thread safety where functions will be considered atomic - or we may wrap things instead. We have to think about that when we get to it.
	def abort(self, error=None):
		self._state.interface.abort()
		self.error = error

	def finish(self):
		self._state.interface.finish()

	def register_work(self):
		self._state.interface.work()


class First_Result(Aggregator):
	value = M.positional(symbol.not_set)

	def aggregate(self, entry):
		self.finish()
		self.value = entry

class Result_List(Aggregator):
	value = M.positional(factory=list)

	def aggregate(self, entry):
		self.register_work()
		self.value.append(entry)

class Result_Set(Aggregator):
	value = M.positional(factory=set)

	def aggregate(self, entry):
		self.register_work()
		self.value.add(entry)

class Sorted_List(Aggregator):
	_value = M.positional(factory=list)
	key = M.positional(None)
	reverse = M.positional(False)

	def aggregate(self, entry):
		self.register_work()
		self._value.append(entry)

	@property
	def value(self):
		return sorted(self._value, key=self.key, reverse=self.reverse)

class Last_Result(Aggregator):
	value = M.positional(symbol.not_set)

	def aggregate(self, entry):
		self.register_work()
		self.value = entry

class Random_Result(Aggregator):
	_options = M.positional(factory=list)

	def aggregate(self, entry):
		self.register_work()
		self._options.append(entry)

	@property
	def value(self):
		if self._options:
			return random.choice(self._options)
		else:
			return symbol.not_set

class Counter(Aggregator):
	value = M.positional(factory=dict)

	def aggregate(self, entry):
		self.register_work()
		self.value[entry] = self.value.get(entry, 0) + 1
