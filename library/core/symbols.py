import sys
#from .factory_helpers import Register_Interface
from . import ABC


CALLING_FRAME = object()	#TODO - Using object before we have a symbol (and it should not be more than one!)
IDENTITY = object()

class Symbol(type):
	def __new__(cls, name, entries=(), module=CALLING_FRAME):
		scope = dict()
		if module is CALLING_FRAME:
			module = sys._getframe(1).f_globals['__name__']

		for entry in entries:
			if isinstance(entry, Enum_Member):
				scope[entry.name] = entry
			else:
				scope[entry.__name__] = entry

		scope['__module__'] = module

		return super().__new__(cls, name, (), scope)

	def __init__(self, *pos, **named):
		pass

	def __call__(self):
		raise Exception('Symbols are singletons')

	def __repr__(self):
		return f'{self.__module__}.{self.__qualname__}'


class Enum(Symbol):
	pass

class Enum_Member:
	def __init__(self, name, value, owner=None):
		self.name = name
		self.value = value
		self.owner = owner

	def __repr__(self):
		if self.value is IDENTITY:
			return f'{self.owner.__module__}.{self.owner.__qualname__}:{self.name}'
		else:
			return f'{self.owner.__module__}.{self.owner.__qualname__}:{self.name}({self.value!r})'


def set_enum_qual_names(target, path=None, skip_root=False):
	if path:
		target.__qualname__ = f'{path}.{target.__name__}'
	else:
		target.__qualname__ = target.__name__

	for child_name, child_ref in target.__dict__.items():
		if child_name.startswith('_'):
			continue

		if isinstance(child_ref, Enum_Member):
			child_ref.owner = target
		elif skip_root:
			set_enum_qual_names(child_ref, None)
		else:
			set_enum_qual_names(child_ref, target.__qualname__)



def S(name, *entries):
	return Symbol(name, entries, module='Symbol')

def Local_Symbol(name, *entries):
	return Symbol(name, entries)	#Module From calling frame

def E(name, *entries):
	return Enum(name, entries, module='Symbol')

def EM(name, value=IDENTITY):
	return Enum_Member(name, value)

