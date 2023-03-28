from . import rudimentary_type_system as RTS
from . import abstract_base_classes as ABC
from .rudimentary_type_system.bases import standard_base as base
import types

#DEPRECATED - we should make an api sub package that have both types for api definition but also some definitions

#TBD - should api use its own conditions or should we utilize the pattern matching features?
#	Currently PM uses api, but it doesn't have to.

#These are simple boolean conditions for use in api definitions - we register them in two places
@ABC.register_class_tree('internal.api.condition', 'internal.condition')
class condition(base, abstract=True):

	def __or__(self, other):
		return any_subcondition(self, other)

	def __and__(self, other):
		return all_subcondition(self, other)

#  ___     _       _ _   _            ___             _ _ _   _
# | _ \_ _(_)_ __ (_) |_(_)_ _____   / __|___ _ _  __| (_) |_(_)___ _ _  ___
# |  _/ '_| | '  \| |  _| \ V / -_) | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
# |_| |_| |_|_|_|_|_|\__|_|\_/\___|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/

class identity(condition):
	identity = RTS.positional()

class instance_of(condition):
	type = RTS.positional()

class subclass_of(condition):
	type = RTS.positional()

class type_identity(condition):
	type = RTS.positional()

class value_equals(condition):
	value = RTS.positional()

#   ___                                _    ___             _ _ _   _
#  / __|___ _ __  _ __  ___ ___ ___ __| |  / __|___ _ _  __| (_) |_(_)___ _ _  ___
# | (__/ _ \ '  \| '_ \/ _ (_-</ -_) _` | | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
#  \___\___/_|_|_| .__/\___/__/\___\__,_|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/
#                |_|

class any_subcondition(condition):
	sub_conditions = RTS.all_positional()

	def __repr__(self):
		return ' | '.join(repr(b) for b in self.sub_conditions)

class all_subconditions(condition):
	sub_conditions = RTS.all_positional()

	def __repr__(self):
		return ' & '.join(repr(b) for b in self.sub_conditions)


#  ___               _                       _
# | _ \___ __ _ _  _(_)_ _ ___ _ __  ___ _ _| |_ ___
# |   / -_) _` | || | | '_/ -_) '  \/ -_) ' \  _(_-<
# |_|_\___\__, |\_,_|_|_| \___|_|_|_\___|_||_\__/__/
#            |_|

@ABC.register_class_tree('internal.api.requirement', 'internal.requirement')
class requirement(base, abstract=True):
	pass

class function(requirement):
	return_requirement = RTS.positional()
	positional_requirements = RTS.all_positional()
	named_requirements = RTS.all_named()
	name = RTS.field()

	def __set_name__(self, target, name):
		self.name = name

	def __get__(self, instance, owner):
		if instance is None:
			return self

		return types.MethodType(self.__call__, instance)

	def __call__(self, *positional, **named):
		target = positional[0]
		raise NotImplementedError(f'Tried calling function {self.name!r} which was not implemented for {target.__class__}')
