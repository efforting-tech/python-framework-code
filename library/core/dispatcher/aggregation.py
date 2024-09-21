from ... import Strict_Symbol as SS	#TODO - we should use strict_symbol in most places
from ..state_machine import State_Manager, Transition
from .. import record as R
import random

AS = SS.Aggregator.Status

class Aggregator(R.Record):
	state_manager = State_Manager(AS, dict(
		abort = Transition(AS.Aborted, {AS.Pending, AS.Working}),
		finish = Transition(AS.Finished, {AS.Pending, AS.Working}),
		work = Transition(AS.Working, {AS.Pending, AS.Working}),
		reset = Transition(AS.Pending),
	))

	_state: R.Field(factory=state_manager) #, repr=False)	#TODO (also note that we may by default hide fields starting with _ using tristate
	error: R.Field() = None

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
	value: R.Field() = SS.Not_Set

	def __iter__(self):
		yield self.value

	def aggregate(self, entry):
		self.finish()
		self.value = entry

class Result_List(Aggregator):
	value: R.Field(factory=list)

	def __iter__(self):
		yield from self.value

	def aggregate(self, entry):
		self.register_work()
		self.value.append(entry)

class Result_Set(Aggregator):
	value: R.Field(factory=set)

	def __iter__(self):
		yield from self.value

	def aggregate(self, entry):
		self.register_work()
		self.value.add(entry)

class Sorted_List(Aggregator):
	_value: R.Field(factory=list)
	key: R.Field() = None
	reverse: R.Field() = False

	def __iter__(self):
		yield from self.value

	def aggregate(self, entry):
		self.register_work()
		self._value.append(entry)

	@property
	def value(self):
		return sorted(self._value, key=self.key, reverse=self.reverse)

class Last_Result(Aggregator):
	value: R.Field() = SS.Not_Set

	def __iter__(self):
		yield self.value

	def aggregate(self, entry):
		self.register_work()
		self.value = entry

class Random_Result(Aggregator):
	_options: R.Field(factory=list)

	def aggregate(self, entry):
		self.register_work()
		self._options.append(entry)

	def __iter__(self):
		yield self.value

	@property
	def value(self):
		if self._options:
			return random.choice(self._options)
		else:
			return SS.Not_Set

class Counter(Aggregator):
	value: R.Field(factory=dict)

	def __iter__(self):
		yield from self.value.items()

	def aggregate(self, entry):
		self.register_work()
		self.value[entry] = self.value.get(entry, 0) + 1
