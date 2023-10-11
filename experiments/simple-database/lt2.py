from efforting.mvp4.data_utils import identity_reference
import threading
import collections.abc as CABC
from efforting.mvp4.symbols import register_symbol
from efforting.mvp4 import pattern_matching as PM
from efforting.mvp4.data_utils import priority_translator as PT
from efforting.mvp4.data_utils.priority_translator import priority_translator



def fmap(function, source):
	for item in map(function, source):
		match item:
			case tuple():
				yield from item
			case _:
				yield item


def hashable(item):
	return isinstance(item, CABC.Hashable)

class bag:
	#Note - this implementation perserves order but this should never be relied upon, this is just an implementation quirk
	def __init__(self, owner, items=None):
		with owner.lock_item(self):
			self._owner = owner
			self._contents = dict()	#value here must be a cardinal number of one or more

			if items:
				self._pour(items)
				owner.register_created_item(self, items)

			else:
				owner.register_created_item(self)


	def _pour(self, items):
		c = self._contents
		for i in items:
			if hashable(i):
				k = i
			else:
				k = identity_reference(i)
			c[k] = c.get(k, 0) + 1

	def pour(self, items):
		with self._owner.lock_item(self):
			self._pour(items)
			self._owner.register_pour(self, items)

	def pop(self):
		with self._owner.lock_item(self):
			c = self._contents
			key, count = next(iter(c.items()))

			if count == 1:
				del self._contents[key]
			else:
				self._contents[key] = count - 1

			self._owner.register_pop(self, key)
			if isinstance(key, identity_reference):
				return key.target
			else:
				return key

	def copy_contents_from(self, *others):
		with self._owner.lock_item(self):
			for i in others:
				self._pour(i)

			self._owner.register_copy_contents_from(self, *others)


	def __contains__(self, item):
		return item in self._contents

	def __len__(self):
		return sum(self._contents.values())

	def __iter__(self):
		for key, count in self._contents.items():
			if isinstance(key, identity_reference):
				key = key.target

			for i in range(count):
				yield key

	def __or__(self, other):
		assert self._owner is other._owner
		new = bag(self._owner)
		new.copy_contents_from(self, other)
		return new



class pending_lock:
	def __init__(self, database, identity):
		self.database = database
		self.identity = identity

	def __enter__(self):
		self.database._pl_lock(self)

	def __exit__(self, et, ev, tb):
		self.database._pl_unlock(self)

class M:
	MUTATION = register_symbol('MUTATION')
	CREATE = MUTATION()
	POP = MUTATION()
	COPY_CONTENTS_FROM = MUTATION()

class database:
	def __init__(self):
		self._lock = threading.Lock()
		self._lock_by_item = dict()
		self._registered_items = set()
		self._mutations = list()
		self.init_priority_translator()

	def init_priority_translator(self):
		t = self._translator = priority_translator()

		def process_tuple(item):
			if item:
				return (1, len(item), *fmap(t.process_item, item))
			else:
				return (5,)

		def process_dict(item):
			if item:
				keys, values = zip(*item.items())
				return (3, len(item), *fmap(t.process_item, keys), *fmap(t.process_item, values))
			else:
				return (4,)	#Empty dict

		def process_int(item):
			return (2, item)

		def process_generic_primitive(item):
			return (item,)

		def process_identity_reference(item):
			return t.process_item(item.target)

		def process_bag(item):
			if item:
				keys, values = zip(*item._contents.items())
				return (6, len(item), *fmap(t.process_item, keys), *fmap(t.process_item, values))
			else:
				return (6, 0)


		t.add_conditional_action(PM.type_identity(tuple), PT.return_processed_item(process_tuple))
		t.add_conditional_action(PM.type_identity(dict), PT.return_processed_item(process_dict))
		t.add_conditional_action(PM.type_identity(identity_reference), PT.return_processed_item(process_identity_reference))
		t.add_conditional_action(PM.type_identity(int), PT.return_processed_item(process_int))
		t.add_conditional_action(PM.type_identity(str), PT.return_processed_item(process_generic_primitive))
		t.add_conditional_action(PM.type_identity(bag), PT.return_processed_item(process_bag))	#Hardcoded for now

	def lock_item(self, item):
		return pending_lock(self, identity_reference(item))

	def _register_mutation(self, item, mutation, *positional):
		print(item, mutation, positional)

	def _register_db_item(self, item):
		self._registered_items.add(identity_reference(item))

	def register_created_item(self, item, *positional, **named):
		with self._lock:
			self._register_db_item(item)
			self._register_mutation(item, M.CREATE, *self._register_one_value(positional), *self._register_one_value(named))


	def _register_one_value(self, value):
		#TODO - we should use a rule based dispatcher here so that we can add custom types
		return self._translator.process_item(value)

	def register_copy_contents_from(self, item, *sources):
		with self._lock:
			self._register_mutation(item, M.COPY_CONTENTS_FROM, *self._register_one_value(sources))

	def register_pop(self, item, element):
		with self._lock:
			self._register_mutation(item, M.POP, element)

	def _pl_lock(self, lock):
		with self._lock:
			if not (lock_ref := self._lock_by_item.get(lock.identity)):
				lock_ref = threading.Lock()
				self._lock_by_item[lock.identity] = lock_ref

			lock_ref.acquire()

	def _pl_unlock(self, lock):
		with self._lock:
			self._lock_by_item.pop(lock.identity).release()




db = database()

car = {'color': 'red'}
b1 = bag(db, (1, 2, car, car))
b2 = bag(db, (1, 2, 3, car))

print(tuple(b1 | b2))


