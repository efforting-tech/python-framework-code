import collections.abc as CABC
import builtins as B

#NOTE: Add move for ordered items? Maybe add baseclass for ordered type
#TODO - replace item with element in many places

class cache:
	def __init__(self):
		self.clear()

	def clear(self):
		self.is_set = False
		self.value = None

	def __bool__(self):
		return self.is_set

	def set(self, value):
		self.value = value
		self.is_set = True


class database_entry:
	creation_hook = None
	mutation_hook = None


class ordered_set(CABC.MutableSet, CABC.MutableSequence, database_entry):
	#Note - we will use _cached_seq to cache the sequential representation of the set. We must remember to clear this using `del _seq` whenever we update the set.
	#Note - CABC will automatically implement union, intersection and difference but it may not be very performant. Therefore we may at some point write our own functions for this.
	def __init__(self, items=None):
		if self.creation_hook:
			self.creation_hook()
		self._data = B.dict()
		self._cached_seq = cache()

		if items:
			self.extend(items)

	@property
	def _seq(self):
		if self._cached_seq:
			return self._cached_seq.value
		else:
			seq = self._seq = B.list(self._data)
			return seq

	@_seq.setter
	def _seq(self, value):
		self._cached_seq.set(value)

	@_seq.deleter
	def _seq(self):
		self._cached_seq.clear()


	def __delitem__(self, index):
		seq = self._seq
		del seq[index]
		self._data = B.dict.fromkeys(seq)
		#No need to clear cache here, deletion is safe
		if self.mutation_hook:
			self.mutation_hook()

	def insert(self, index, value):
		seq = self._seq
		seq.insert(index, value)
		self._data = B.dict.fromkeys(seq)
		del self._seq	#Note - additive mutation could be duplicate key, clear cache
		if self.mutation_hook:
			self.mutation_hook()

	def extend(self, items):
		for element in items:
			self._data[element] = None
		del self._seq		#Clear cache
		if self.mutation_hook:
			self.mutation_hook()

	def __getitem__(self, index):
		return self._seq[index]

	def __len__(self):
		return len(self._data)

	def __setitem__(self, index, value):
		seq = self._seq
		seq[index] = value
		self._data = B.dict.fromkeys(seq)
		del self._seq	#Note - mutation could be duplicate key, clear cache
		if self.mutation_hook:
			self.mutation_hook()

	def add(self, value):
		self._data[value] = None
		del self._seq		#Clear cache
		if self.mutation_hook:
			self.mutation_hook()

	def discard(self, value):
		self._data.pop(value, None)
		del self._seq		#Clear cache
		if self.mutation_hook:
			self.mutation_hook()

class unordered_set(CABC.MutableSet, database_entry):
	def __init__(self, init=None):
		if self.creation_hook:
			self.creation_hook()

		if init:
			self._data = B.set(init)
		else:
			self._data = B.set()


	def __contains__(self, element):
		return element in self._data

	def __len__(self):
		return len(self._data)

	def __iter__(self):
		return iter(self._data)

	def add(self, element):
		self._data.add(element)
		if self.mutation_hook:
			self.mutation_hook()

	def discard(self, element):
		self._data.discard(element)
		if self.mutation_hook:
			self.mutation_hook()


class ordered_dict(CABC.MutableMapping, CABC.MutableSequence, database_entry):
	def __init__(self, *positional, **named):
		if self.creation_hook:
			self.creation_hook()

		self._cached_seq = cache()
		self._data = B.dict()

		if len(positional) >= 1:
			self._data.update(*positional)

		if named:
			self._data.update(named)

	@property
	def _seq(self):
		if self._cached_seq:
			return self._cached_seq.value
		else:
			seq = self._seq = B.list(self._data.items())
			return seq

	@_seq.setter
	def _seq(self, value):
		self._cached_seq.set(value)

	@_seq.deleter
	def _seq(self):
		self._cached_seq.clear()



	def __delitem__(self, key):
		del self._data[key]
		if self.mutation_hook:
			self.mutation_hook()

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value
		if self.mutation_hook:
			self.mutation_hook()

	def __iter__(self):
		return iter(self._data)

	def __len__(self):
		return len(self._data)

	def insert(self, index, key, value):
		seq = self._seq
		seq.insert(index, (key, value))
		self._data = B.dict(seq)
		del self._seq	#Note - additive mutation could be duplicate key, clear cache
		if self.mutation_hook:
			self.mutation_hook()

class unordered_dict(CABC.MutableMapping, database_entry):
	def __init__(self, *positional, **named):
		if self.creation_hook:
			self.creation_hook()

		self._data = B.dict()

		if len(positional) >= 1:
			self._data.update(*positional)

		if named:
			self._data.update(named)

	def __delitem__(self, key):
		del self._data[key]
		if self.mutation_hook:
			self.mutation_hook()

	def __getitem__(self, key):
		return self._data[key]

	def __setitem__(self, key, value):
		self._data[key] = value
		if self.mutation_hook:
			self.mutation_hook()

	def __iter__(self):
		return iter(self._data)

	def __len__(self):
		return len(self._data)

class list(CABC.MutableSequence, database_entry):
	def __init__(self, items=None):
		if self.creation_hook:
			self.creation_hook()

		self._data = B.list()
		if items:
			self._data.pour(items)

	def __contains__(self, item):
		return item in self._data

	def __getitem__(self, index):
		return self._data[index]

	def __setitem__(self, index, value):
		self._data[index] = value
		if self.mutation_hook:
			self.mutation_hook()

	def __delitem__(self, index):
		del self._data[index]
		if self.mutation_hook:
			self.mutation_hook()

	def insert(self, index, value):
		self._data.insert(index, value)
		if self.mutation_hook:
			self.mutation_hook()

	def __len__(self):
		return len(self._data)

	def __iter__(self):
		return iter(self._data)


class bag(CABC.Container, CABC.Iterable, database_entry):
	#Note - this implementation perserves order but this should never be relied upon, this is just an implementation quirk
	def __init__(self, items=None):
		if self.creation_hook:
			self.creation_hook()

		self._data = B.list()
		if items:
			self._data.pour(items)

	def pour(self, items):
		self._data.extend(items)
		if self.mutation_hook:
			self.mutation_hook()

	def __contains__(self, item):
		return item in self._data

	def __len__(self):
		return len(self._data)

	def __iter__(self):
		return iter(self._data)

	def add(self, item):
		self._data.append(item)
		if self.mutation_hook:
			self.mutation_hook()

	def remove_all(self, item):
		self._data = [i for i in self._data if i != item]
		if self.mutation_hook:
			self.mutation_hook()
