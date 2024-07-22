from itertools import chain
import sys
from .factory import Evaluate_In_Scope
from .. import symbol
from .. import ABC


#BUG - one can specify all.named/positional more than once
#BUG - one can assign init even in situations where init won't be utilized

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

#TODO - should TD_LUT be used? - we should probably have some sort of common interface for introspection. the TD_LUT idea is ok but we should remove it from rudimentary and make it its own thing
#	though maybe we should do this via data descriptors
#TD_LUT = dict()


# class Type_Definition:
# 	def __init__(self, name, positional, named, bases):
# 		self.name = name
# 		self.positional = positional
# 		self.named = named
# 		self.bases = bases


def iter_names(target_type):
		bo = tuple(reversed(target_type.mro()))
		for base in bo:
			for dd in base.__dict__.values():
				if isinstance(dd, ABC.Record.Data_Descriptor):
					yield dd.name


def iter_type_members(target_type):
	for n in iter_names(target_type):
		yield getattr(target_type, n)

def iter_instance_members_and_values(target_instance, default=None):
	for m in iter_type_members(type(target_instance)):
		yield m, getattr(target_instance, m.descriptor.name, default)

#TODO - maybe rename to rudimentary record?
class Abstract_Record(ABC.Record):
	def __init__(self, *positional, **named):
		positional = list(positional)
		#bo = tuple(reversed(type(self).mro()))

		original_named = dict(named)
		names = tuple(iter_names(type(self)))

		for n in names:
			dd = getattr(type(self), n).descriptor

			if dd.kind is symbol.argument.all.positional:
				setattr(self, n, tuple(positional))
				positional.clear()

			elif dd.kind is symbol.argument.all.named:
				setattr(self, n, dict(named))
				named.clear()

			elif dd.kind is symbol.argument.positional_or_named:
				if positional:

					#TODO - we should make sure we are compatible with python kinds of pos, pos/name, name_only
					if n in named:
						setattr(self, n, named.pop(n))
					else:
						setattr(self, n, positional.pop(0))

					#assert n not in original_named	#TODO - figure out if we need original here or not
					#setattr(self, n, positional.pop(0))
				elif n in named:
					setattr(self, n, named.pop(n))
				else:
					match dd.init:
						case ABC.Factory():
							dd.init(dd, self)
						case Value(value):
							setattr(self, n, value)
						case nothing if nothing is None:
							setattr(self, n, None)

						case unhandled:
							raise Exception(unhandled)	#TODO - proper exception

			assert (not dd.required) or hasattr(self, n)	#TODO - proper exception

		assert not positional #TODO - proper exception
		assert not named #TODO - proper exception


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

class Bound_Data_Descriptor(ABC.Record.Data_Descriptor):
	def __init__(self, descriptor, owner):
		self.descriptor = descriptor
		self.owner = owner

	def __repr__(self):
		cn = f'{self.owner.__module__}.{self.owner.__qualname__}' #TODO - use utility function for formatting class name
		return f'<Member {self.descriptor.name!r} of class {cn!r}>'

class Data_Descriptor(ABC.Record.Data_Descriptor):
	def __init__(self, name, init=None, required=False, kind=symbol.argument.positional_or_named, repr=True):
		self.name = name
		self.init = init
		self.required = required
		self.kind = kind
		self.repr = repr

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

def create_record(name, positional=None, named=None, bases=None, evaluation_scope=None, local_updates=None, prepared_scope=None):
	scope = prepared_scope if prepared_scope is not None else dict()

	if positional:
		for member in positional:
			scope[member] = Data_Descriptor(member, required=True)

	if named:
		for member, init_or_kind in named.items():
			if isinstance(init_or_kind, Value):
				scope[member] = Data_Descriptor(member, init_or_kind)
			elif isinstance(init_or_kind, str):
				scope[member] = Data_Descriptor(member, Evaluate_In_Scope(init_or_kind, evaluation_scope, local_updates))
			elif init_or_kind in symbol.argument.all:
				scope[member] = Data_Descriptor(member, kind=init_or_kind)
			elif init_or_kind is None:
				scope[member] = Data_Descriptor(member)
			else:
				raise Exception(member, init_or_kind)

	type_bases = (Abstract_Record,) if not bases else bases
	result = type(name, type_bases, scope)
	#TD_LUT[result] = Type_Definition(name, positional, named, bases)
	return result

def define_simple_record(name, *positional, **named):
	target_scope = sys._getframe(1).f_locals

	assert name not in target_scope	#TODO - proper exception
	target_scope[name] = create_record(name, positional, named, evaluation_scope=target_scope, prepared_scope=dict(__module__=target_scope['__name__']))

def define_record(name, positional=None, named=None, bases=None, evaluation_scope=None, local_updates=None):
	target_scope = sys._getframe(1).f_locals

	assert name not in target_scope	#TODO - proper exception
	target_scope[name] = create_record(name, positional, named, bases=bases, evaluation_scope=target_scope, local_updates=local_updates, prepared_scope=dict(__module__=target_scope['__name__']))

class Value:
	__match_args__ = ('value',)
	def __init__(self, value):
		self.value = value
