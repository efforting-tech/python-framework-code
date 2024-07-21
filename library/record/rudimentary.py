from itertools import chain
import sys
from .factory import Evaluate_In_Scope

#TODO - we may want to put all exceptions in one place later and possibly name them better
class No_Such_Member_Exception(AttributeError):
	def __init__(self, target, member):
		owner = type(target)
		cn = f'{owner.__module__}.{owner.__qualname__}' #TODO - use utility function for formatting class name
		super().__init__(f'The {cn!r} instance 0x{id(target):x} does not have any member {member!r}.')

#TODO - we may want to put all exceptions in one place later and possibly name them better
class Member_Not_Set_Exception(AttributeError):
	def __init__(self, target, member):
		owner = type(target)
		cn = f'{owner.__module__}.{owner.__qualname__}' #TODO - use utility function for formatting class name
		super().__init__(f'The member {member!r} of the {cn!r} instance 0x{id(target):x} is not set.')


TD_LUT = dict()

class Type_Definition:
	def __init__(self, name, positional, named, bases):
		self.name = name
		self.positional = positional
		self.named = named
		self.bases = bases

def iter_positional(target_type):
		bo = tuple(reversed(target_type.mro()))
		for base in bo:
			if td := TD_LUT.get(base):
				if td.positional:
					yield from td.positional


def iter_named(target_type):
		bo = tuple(reversed(target_type.mro()))
		for base in bo:
			if td := TD_LUT.get(base):
				if td.named:
					yield from td.named

def iter_type_members(target_type):
	for n in chain(iter_positional(target_type), iter_named(target_type)):
		yield getattr(target_type, n)

def iter_instance_members_and_values(target_instance, default=None):
	for m in iter_type_members(type(target_instance)):
		yield m, getattr(target_instance, m.descriptor.name, default)

class Abstract_Record:
	def __init__(self, *positional, **named):
		positional = list(positional)
		#bo = tuple(reversed(type(self).mro()))
		positional_names = tuple(iter_positional(type(self)))
		named_names = tuple(iter_named(type(self)))

		for n in positional_names:
			if not positional:
				break

			setattr(self, n, positional.pop(0))

		for n, v in named.items():
			assert not hasattr(self, n)	#TODO - proper exception
			setattr(self, n, v)

		assert not positional #TODO - proper exception

		for n in chain(positional_names, named_names):
			dd = getattr(type(self), n).descriptor

			if not hasattr(self, n):
				if dd.init:
					dd.init(dd, self)

			assert (not dd.required) or hasattr(self, n)	#TODO - proper exception



	def __setattr__(self, name, value):
		if (dd := getattr(type(self), name, None)) and isinstance(dd, Bound_Data_Descriptor):
			dd.descriptor.__set__(self, value)
		else:
			raise No_Such_Member_Exception(self, name)

	def __getattr__(self, name):
		if (dd := getattr(type(self), name, None)) and isinstance(dd, Bound_Data_Descriptor):
			return dd.descriptor.__get__(self, dd.owner)
		else:
			raise No_Such_Member_Exception(self, name)

	def __delattr__(self, name):
		if (dd := getattr(type(self), name, None)) and isinstance(dd, Bound_Data_Descriptor):
			return dd.descriptor.__delete__(self)
		else:
			raise No_Such_Member_Exception(self, name)

class Bound_Data_Descriptor:
	def __init__(self, descriptor, owner):
		self.descriptor = descriptor
		self.owner = owner

	def __repr__(self):
		cn = f'{self.owner.__module__}.{self.owner.__qualname__}' #TODO - use utility function for formatting class name
		return f'<Member {self.descriptor.name!r} of class {cn!r}>'

class Data_Descriptor:
	def __init__(self, name, init=None, required=False):
		self.name = name
		self.init = init
		self.required = required

	def __get__(self, instance, owner):
		if instance is None:
			return Bound_Data_Descriptor(self, owner)
		else:
			try:
				return instance.__dict__[self.name]
			except KeyError as ke:
				raise Member_Not_Set_Exception(instance, self.name) from ke

	def __set__(self, instance, value):
		instance.__dict__[self.name] = value

	def __delete__(self, instance):
		try:
			del instance.__dict__[self.name]
		except KeyError as ke:
			raise Member_Not_Set_Exception(instance, self.name) from ke

def create_record(name, positional=None, named=None, bases=None, evaluation_scope=None, local_updates=None):
	scope = dict()

	if positional:
		for member in positional:
			scope[member] = Data_Descriptor(member, required=True)

	if named:
		for member, init in named.items():
			scope[member] = Data_Descriptor(member, Evaluate_In_Scope(init, evaluation_scope, local_updates))

	type_bases = (Abstract_Record,) if not bases else bases
	result = type(name, type_bases, scope)
	TD_LUT[result] = Type_Definition(name, positional, named, bases)
	return result

def define_simple_record(name, *positional, **named):
	target_scope = sys._getframe(1).f_locals

	assert name not in target_scope	#TODO - proper exception
	target_scope[name] = create_record(name, positional, named, evaluation_scope=target_scope)
