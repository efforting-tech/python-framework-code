from collections import Counter
import sys

MISS = object()

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
	to_export = None

	def __enter__(self):
		assert self.to_export is None
		self.to_export = dict(sys._getframe(1).f_locals)
		return self

	def __exit__(self, et, ev, tb):
		target = sys._getframe(1).f_locals
		keys = set(target)

		for key, value in self.to_export.items():
			keys.discard(key)
			target[key] = value

		for key in keys:	#Discard remaining
			del target[key]

		self.to_export = None

	def export(self, name, value):
		self.to_export[name] = value

