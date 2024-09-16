from ..member import utils as MU
from .. import member as M
from ..rudimentary import Abstract_Record, Data_Descriptor, Abstract_Sequence, Abstract_Mapping
from ... import ABC, Symbol
from ...introspection import stack_limit
from ...symbol_factory import Local_Symbol

import itertools


#The idea here is to make use of the many ideas for various record definition systems from prior experiments
#But for now the rudimentary system is probably powerful enough that we can have this system here just as a convenient way of defining classes

def get_name(target):
	for n in ('__qualname__', '__name__', 'name'):
		if v := getattr(target, n, None):
			return v


#TODO - move
def iter_object_using_type(target_object, target_type, default=Symbol.Miss):
	for key in target_type.__dict__:	#NOTE - we can't use dir because it will sort things
		yield key, getattr(target_object, key, default)

def iter_type(target, default=Symbol.Miss):
	for cls in reversed(target.mro()):
		yield from iter_object_using_type(target, cls, default)


REPR_STACK_LIMIT = stack_limit(2)

class Dynamic_Structure:
	pass

class Structure(Abstract_Record):
	def __init_subclass__(cls):
		all_names = dict()

		for key, value in iter_type(cls):
			if isinstance(value, ABC.Record.Member):
				all_names[key] = value

		for key, value in all_names.items():
				#TODO - properly reflect these kinds
				# if isinstance(value, M.positional):
				# 	kind = symbol.argument.positional_or_named
				# elif isinstance(value, M.named):
				# 	kind = symbol.argument.positional_or_named


				#TODO convert to match?
				if isinstance(value, M.all_positional):
					setattr(cls, key, Data_Descriptor(key, kind=Symbol.Argument.All.Positional, repr=value.repr, repr_condition=value.repr_condition))

				elif isinstance(value, M.all_named):
					setattr(cls, key, Data_Descriptor(key, kind=Symbol.Argument.All.Named, repr=value.repr, repr_condition=value.repr_condition))

				elif value.factory and value.default is None:	#TODO we must decide how to be able to create required positionals by M.positional() vs M.positional(...)
					setattr(cls, key, Data_Descriptor(key, init=MU.factory(value.factory), repr=value.repr, repr_condition=value.repr_condition))

				elif value.default is not None and not value.factory:
					setattr(cls, key, Data_Descriptor(key, init=MU.constant(value.default), repr=value.repr, repr_condition=value.repr_condition))

				elif value.default is None and not value.factory:
					setattr(cls, key, Data_Descriptor(key, repr=value.repr, repr_condition=value.repr_condition))


				else:
					raise Exception(key, value.default)	#TODO - proper exception


		cls.__match_args__ = tuple(n for n, d in iter_type(cls) if isinstance(d, ABC.Record.Data_Descriptor))



	def __repr__(self):
		MISS = Local_Symbol('MISS')
		with REPR_STACK_LIMIT:
			members = dict((n, f) for n, f in iter_type(type(self)) if isinstance(f, ABC.Record.Data_Descriptor) and f.descriptor.repr)
			try:
				def fval(n):
					if (value := getattr(self, n, MISS)) is MISS:
						return 'N/A'
					if isinstance(value, type):
						if n := get_name(value):
							return f'<{value.__qualname__}>'

					elif callable(value):
						if n := get_name(value):
							return f'𝑓<{get_name(value)}>'

					return repr(value)

				def should_include(f, n):
					if not f.descriptor.repr_condition:
						return True

					value = getattr(self, n, Symbol.Miss)
					return f.descriptor.repr_condition(value)




				inner = ', '.join(f'{n}={fval(n)}' for n, f in members.items() if should_include(f, n))
				return f'{self.__class__.__qualname__}({inner})'
			except RecursionError:
				return '\N{HORIZONTAL ELLIPSIS}'

class Sequence(Structure, Abstract_Sequence):
	#TODO - handle long by [1, 2, ..., -2, -1]
	def __repr__(self):
		MISS = Local_Symbol('MISS')
		with REPR_STACK_LIMIT:
			members = dict((n, f) for n, f in iter_type(type(self)) if isinstance(f, ABC.Record.Data_Descriptor) and f.descriptor.repr)
			try:
				def fval(n):
					if (value := getattr(self, n, MISS)) is MISS:
						return 'N/A'
					else:
						return repr(value)

				inner = ', '.join(itertools.chain(
					(map(repr, self)),
					(f'{n}={fval(n)}' for n, f in members.items()),
				))
				return f'{self.__class__.__qualname__}({inner})'
			except RecursionError:
				return '\N{HORIZONTAL ELLIPSIS}'

class Mapping(Structure, Abstract_Mapping):
	#TODO - handle long by [1, 2, ..., -2, -1]
	def __repr__(self):
		MISS = Local_Symbol('MISS')
		with REPR_STACK_LIMIT:
			members = dict((n, f) for n, f in iter_type(type(self)) if isinstance(f, ABC.Record.Data_Descriptor) and f.descriptor.repr)
			try:
				def fval(n):
					if (value := getattr(self, n, MISS)) is MISS:
						return 'N/A'
					else:
						return repr(value)

				inner = ', '.join(itertools.chain(
					(f'{k!r}: {v!r}' for k, v in self.items()),
					(f'{n}={fval(n)}' for n, f in members.items()),
				))
				return f'{self.__class__.__qualname__}({inner})'
			except RecursionError:
				return '\N{HORIZONTAL ELLIPSIS}'
