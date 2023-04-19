from ..symbols import create_symbol
from collections import Counter
import sys


MISS = create_symbol('internal.miss')

#TODO - complementing mutating interface
class attribute_dict_ro_access:
	def __init__(self, target):
		self._target = target

	def __getattr__(self, key):
		try:
			return self._target[key]
		except KeyError:
			raise AttributeError(f'{self.__class__.__qualname__}({self._target}) does not contain the key {key}')



#TODO - how do these compare with some of the conditions and API requirements we have? Can we harmonize?
def is_type(item, type_or_tuple):
	item_type = type(item)
	if isinstance(type_or_tuple, (tuple, list)):
		for sub_type in type_or_tuple:
			if item_type is sub_type:
				return True
	else:
		if item_type is type_or_tuple:
			return True

	return False

#TODO - how do these compare with some of the conditions and API requirements we have? Can we harmonize?
def is_subclass(item, type_or_tuple):
	return isinstance(item, type) and issubclass(item, type_or_tuple)


def strip_sequence(item, condition=bool):
	start = None
	end = None
	for index, sub_item in enumerate(item):
		if condition(sub_item):
			if start is None:
				start = index
			end = index + 1

	if start is None and end is None:
		return item.__class__()

	return item[start:end]



#TODO - write both tests and docs for these things
class stack_limit:

	def __init__(self, depth):
		self.depth = depth
		self.frame_counter = Counter()

	def __enter__(self):
		calling_frame = sys._getframe(1)
		key = calling_frame.f_code, calling_frame.f_lineno
		count = self.frame_counter[key] = self.frame_counter[key] + 1
		if count > self.depth:
			self.frame_counter[key] = self.frame_counter[key] - 1
			raise RecursionError('max_stack depth exceeded')


	def __exit__(self, et, ev, tb):
		calling_frame = sys._getframe(1)
		key = calling_frame.f_code, calling_frame.f_lineno
		self.frame_counter[key] = self.frame_counter[key] - 1

class stack:
	def __init__(self, target, *updates, **named_updates):
		self.target = target
		self.updates = dict()
		for u in updates:
			self.updates.update(u)
		self.updates.update(named_updates)
		self.previous = None

	def stack(self, **named):
		return self.__class__(self.target, **named)

	def get(self, key):
		return self.updates[key]

	def set_and_return(self, key, value):
		self.updates[key] = value
		return value

	def __enter__(self):
		assert self.previous is None
		self.previous = tuple(self.target.get(key, MISS) for key in self.updates)
		self.target.update(self.updates)

	def __exit__(self, et, ev, tb):
		for key, value in zip(self.updates, self.previous):
			if value is MISS:
				del self.target[key]
			else:
				self.target[key] = value


class attribute_stack:
	def __init__(self, target, *updates, **named_updates):
		self.target = target
		self.updates = dict()
		for u in updates:
			self.updates.update(u)
		self.updates.update(named_updates)
		self.previous = None

	def __enter__(self):
		assert self.previous is None
		self.previous = tuple(getattr(self.target, key, MISS) for key in self.updates)
		for key, value in self.updates.items():
			setattr(self.target, key, value)

	def __exit__(self, et, ev, tb):
		for key, value in zip(self.updates, self.previous):
			if value is MISS:
				delattr(self.target, key)
			else:
				setattr(self.target, key, value)




#TODO - write examples for this and explain why this can be useful
class subscope:
	#TODO - maybe rename?
	initial_scope = None
	initial_frame = None


	def __enter__(self):
		assert self.initial_scope is None
		self.initial_scope = dict(sys._getframe(1).f_locals)
		self.initial_frame = sys._getframe(1)

		return self

	def __exit__(self, et, ev, tb):
		target = self.initial_frame.f_locals
		keys = set(target)

		for key, value in self.initial_scope.items():
			keys.discard(key)
			target[key] = value

		for key in keys:	#Discard remaining
			del target[key]

		self.initial_scope = None


	def get_pending(self, ignore=()):	#Returns things defined in subscope
		result = dict()
		pre_existing = set(self.initial_scope) | set(ignore)
		for key, value in self.initial_frame.f_locals.items():
			if key not in pre_existing:
				result[key] = value
		return result


	def export(self, name, value):
		self.initial_scope[name] = value

