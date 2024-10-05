from dataclasses import dataclass
import types

# The interface verification system in this file is intended to ensure that classes meet certain requirements (methods or members) defined by interfaces. Although not fully implemented, the idea is to allow:
#     Interface Definition: Interfaces can define required methods or attributes that classes must implement. These are likely represented as objects like Interface and Interface_Branch.
#     Class-Interface Association: Classes are associated with interfaces using decorators (e.g., @Require_Interfaces(IFA)), which marks the class as needing to comply with the specified interface(s).
#     Verification: Upon class definition or instantiation, a verification process checks whether the class implements the required methods or members from its associated interfaces. This could involve using tools like inspect.signature to check method signatures or verifying that specific members exist.
#     Configurable Verification: The actual enforcement of these checks might only happen when certain flags or configurations are set, making the verification process flexible. For instance, it might serve as a linting mechanism during development but be skipped in production unless explicitly configured.
# This system allows for self-testing of class compliance with interfaces, ensuring that requirements are met while providing the flexibility to enable or disable verification as needed.
# This design supports dynamic class management, interface verification, and configurable subclass behavior with hooks.
# This explanation was written by ChatGPT on October 3, 2024.


class ID_LUT_KeyError(KeyError):
	def __init__(self, target, key):
		super().__init__(f'{target!r} does not contain the id of {key!r}')

class Meta_LUT_KeyError(KeyError):
	def __init__(self, target, key, property_key):
		super().__init__(f'{target!r} does not contain the sub property {property_key!r} of the id for {key!r}')

class Meta_LUT_MalformedKeyError(KeyError):
	def __init__(self, target, key):
		super().__init__(f'Malformed key used when accessing {target!r}. Key should be a tuple of an id key and a property key but got {key!r}')

class Type_Hook_LUT_KeyError(KeyError):
	def __init__(self, target, key):
		super().__init__(f'{target!r} does not contain any hooks for {key!r}')

class ID_LUT:
	'Associates objects with values using their id() as the key to avoid issues with object garbage collection. Provides fast lookups, stores the object and its value.'
	def __init__(self):
		self.LUT = dict()

	def __setitem__(self, key, value):
		key_id = id(key)
		self.LUT[key_id] = key, value	#We keep a reference to prevent gc of key but we use id for key

	def __getitem__(self, key):
		key_id = id(key)
		if entry := self.LUT.get(key_id):
			return entry[1]
		else:
			raise ID_LUT_KeyError(self, key)

	def __delitem__(self, key):
		key_id = id(key)
		if not self.LUT.pop(key_id, None):
			raise ID_LUT_KeyError(self, key)

	def __contains__(self, key):
		key_id = id(key)
		return key_id in self.LUT

	def get(self, key, default=None):
		key_id = id(key)
		if entry := self.LUT.get(key_id):
			return entry[1]
		else:
			return default

class Meta_LUT:
	'Associates objects, using their id() as the key, with a dictionary of sub-entries. To access or modify this collection, the key must be a tuple consisting of the object and a sub-key. This allows grouping multiple entries under a single object while using individual sub-keys for retrieval or storage.'
	def __init__(self):
		self.LUT = dict()

	def __setitem__(self, key, value):
		try:
			target, sub_key = key
		except ValueError:
			raise Meta_LUT_MalformedKeyError(self, key) from None
		key_id = id(target)

		if sub_mapping := self.LUT.get(key_id):
			sub_mapping[sub_key] = value
		else:
			self.LUT[key_id] = key, {sub_key: value}

	def __getitem__(self, key):
		try:
			target, sub_key = key
		except ValueError:
			raise Meta_LUT_MalformedKeyError(self, key) from None
		key_id = id(target)

		if entry := self.LUT.get(key_id):
			sub_mapping = entry[1]
			if sub_key in sub_mapping:
				return sub_mapping[sub_key]
			else:
				raise Meta_LUT_KeyError(self, target, sub_key)

		else:
			raise Meta_LUT_KeyError(self, target, sub_key)

	def __delitem__(self, key):
		try:
			target, sub_key = key
		except ValueError:
			raise Meta_LUT_MalformedKeyError(self, key) from None
		key_id = id(target)

		if entry := self.LUT.get(key_id):
			if not entry[1].pop(sub_key, None):
				raise Meta_LUT_KeyError(self, target, sub_key)
		else:
			raise Meta_LUT_KeyError(self, target, sub_key)


	def __contains__(self, key):
		try:
			target, sub_key = key
		except ValueError:
			raise Meta_LUT_MalformedKeyError(self, key) from None
		key_id = id(target)

		if entry := self.LUT.get(key_id):
			return sub_key in entry[1]
		else:
			return False

	def get(self, key, default=None):
		try:
			target, sub_key = key
		except ValueError:
			raise Meta_LUT_MalformedKeyError(self, key) from None
		key_id = id(target)

		if entry := self.LUT.get(key_id):
			return entry[1].get(sub_key, default)
		else:
			return default


class Type_Collection_LUT:
	'Associates types with an ordered set of entries. When enumerating, it respects inheritance, yielding entries from parent types first (reverse MRO).'

	def __init__(self):
		self.LUT = dict()

	def __setitem__(self, key, entry):
		if (existing := self.LUT.get(key)) is None:
			self.LUT[key] = dict.fromkeys((entry,), True)
		else:
			existing[entry] = True

	def __getitem__(self, key):
		if entry := self.LUT.get(key):
			return entry.keys()
		else:
			raise Type_Hook_LUT_KeyError(self, key)

	def __delitem__(self, entry):
		to_del = list()
		for key, entries in self.LUT.items():
			if entry in entries:
				to_del.append((entries, entry))

		for entries, entry in to_del:
			del entries[entry]

	def __contains__(self, key):
		return key in self.LUT

	def get(self, key, default=None):
		if entry := self.LUT.get(key):
			return entry.keys()
		else:
			return default


	def walk_entries(self, type_key):
		for base in reversed(type_key.mro()):
			yield from self.get(base, ())


@dataclass
class Pending_Type_LUT_Entry:
	LUT: Type_Collection_LUT
	entries: list

	def __call__(self, target_type):
		for entry in self.entries:
			self.LUT[entry] = target_type
		return target_type


class Type_Hook_LUT(Type_Collection_LUT):
	def hook(self, *type_list):
		return Pending_Type_LUT_Entry(self, type_list)



# class A:
# 	pass

# class B(A):
# 	pass

# @INTERFACES.hook(A)
# def init_thing(cls):
# 	print('Init subclass of', cls)

# @INTERFACES.hook(A)
# def init_thing2(cls):
# 	print('More Init subclass of', cls)

# @INTERFACES.hook(B)
# def init_thing3(cls):
# 	print('Even More Init subclass of', cls)


# for hook in INTERFACES.walk_hooks(A):
# 	hook('test')

# del INTERFACES[init_thing2]
# print('----')



#for hook in INTERFACES.walk_hooks(B):
	#hook('test')



#OUTPUT
# Init subclass of test
# More Init subclass of test
# ----
# Init subclass of test
# Even More Init subclass of test



class Interface_Condition:
	pass


def immutable_record(cls):
	return dataclass(frozen=True)(cls)

@immutable_record
class Interface_Branch(Interface_Condition):
	branches: tuple

@immutable_record
class Interface(Interface_Condition):
	name: str

	def __or__(self, other):
		return Interface_Branch((self, other))




# class chain_actions:
# 	def __init__(self, *chain):
# 		self.chain = chain

# 	def __call__(self, *positional, **named):
# 		for link in self.chain:
# 			link(*positional, **named)



RAISE_EXCEPTION = object()

def popattr(target, name, default=RAISE_EXCEPTION):
	if hasattr(target, name):
		value = getattr(target, name)
		delattr(target, name)
		return value
	elif default is RAISE_EXCEPTION:
		raise AttributeError(f'Required attribute {name!r} was not set for {target!r}')	#TODO - custom exception
	else:
		return default


META = Meta_LUT()
FIELDS = object()

SUBCLASS_HOOKS = Type_Hook_LUT()

class R:

	class Record:
		def __init_subclass__(cls):
			print('INIT', cls)
			fields = dict()

			#Collate existing fields
			for base in cls.mro():
				if meta := META.get((cls, FIELDS)):
					fields.update(meta)

			#Create new fields based on annotations
			if anno := popattr(cls, '__annotations__', None):
				for name, definition in anno.items():
					fields[name] = R.Field(name)	#TODO - utilize definition

					#We should create a system that contains everything we need and all hooks for customization


			#Use fields to create members
			for name, field in fields.items():
				setattr(cls, name, field.create_data_descriptor(cls, name))

			META[cls, FIELDS] = fields

			#Additional subclass hooks
			for hook in SUBCLASS_HOOKS.walk_entries(cls):
				hook(cls)

		def __init__(self):
			if meta := META.get((type(self), FIELDS)):
				for name, field in meta.items():
					field.init_instance(self, name)

	@dataclass
	class Field:
		name: str

		def init_instance(self, target, name):
			pass

		def create_data_descriptor(self, target, name):
			return R.Data_Descriptor(name, self)



	class Data_Descriptor:
		def __init__(self, name, field):
			self.name = name
			self.field = field

		def __get__(self, instance, owner):
			if instance:
				try:
					return instance.__dict__[self.name]		#NOTE - different data descriptors may rely on Field or have other mechanics in place
				except KeyError as ke:
					raise AttributeError(f'Attribute {self.name!r} of {instance} is not set') from ke
			else:
				return R.Bound_Data_Descriptor(owner, self)

		def __repr__(self):
			return f'<Unbound member {self.name!r}>'



	class Bound_Data_Descriptor:
		def __init__(self, owner, descriptor):
			self.owner = owner
			self.descriptor = descriptor

		def __repr__(self):
			return f'<Bound member {self.descriptor.name!r} of {self.owner}>'




def Require_Interfaces(*interfaces):
	return INTERFACE_LUT.decorate(*interfaces)


@dataclass
class Pending_Interface_LUT_Entry:
	LUT: Type_Collection_LUT
	entries: list

	def __call__(self, target):
		self.LUT.register(target, *self.entries)

		for interface in INTERFACE_LUT.walk_entries(target):
			#Just show interfaces - plan is to actually verify them (depending on mode) either by requirements of callables or also checking signature (more fore linting than runtime)
			print(f'INTERFACE - {target} uses interface {interface}')

		return target


class Interface_LUT(Type_Collection_LUT):

	def decorate(self, *entry_list):
		return Pending_Interface_LUT_Entry(self, entry_list)

	def register(self, target_type, *entry_list):
		for entry in entry_list:
			self[target_type] = entry


INTERFACE_LUT = Interface_LUT()


IFA = Interface('IFA')
IFB = Interface('IFB')


@Require_Interfaces(IFA)
class test(R.Record):
	member: str


#NOTE - initially we would call Verify_Interfaces using a subclass init hook but that doesn't work since the decorator is run after class is defined
#		instead we will make sure that when Require_Interfaces instance is being called we also verify. This will lead to double verification but we could use a cache

# @SUBCLASS_HOOKS.hook(test)
# def Verify_Interfaces(cls):
# 	for interface in INTERFACE_LUT.walk_entries(cls):
# 		print(f'INTERFACE - {cls} uses interface {interface}')

# Verify_Interfaces(test)	#Explicitly the thing for the base class

print(test.member)

@Require_Interfaces(IFB)
class subtest(test):
	member: int



print(subtest.member)
s = subtest()

#print(s.member)

#help(R.Field)

print(META.get((subtest, FIELDS)))





for e in INTERFACE_LUT.walk_entries(subtest):
	print(e)





#print(R.Field(123))