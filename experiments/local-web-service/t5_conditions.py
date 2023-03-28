from efforting.mvp4.presets.text_processing import *

def instantiate(t):
	return t()

ANYTHING = register_symbol('ANYTHING')

#These are simple boolean conditions for use in api definitions - we register them in two places
#@ABC.register_class_tree('internal.api.condition', 'internal.condition')
class condition(public_base, abstract=True):
	def __neg__(self, other):
		return negated(other)

	def __or__(self, other):
		return any_subcondition(self, other)

	def __and__(self, other):
		return all_subconditions(self, other)



class negated(condition):
	sub_condition = RTS.positional()

	def __neg__(self, other):
		return self.sub_condition


#  ___     _       _ _   _            ___             _ _ _   _
# | _ \_ _(_)_ __ (_) |_(_)_ _____   / __|___ _ _  __| (_) |_(_)___ _ _  ___
# |  _/ '_| | '  \| |  _| \ V / -_) | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
# |_| |_| |_|_|_|_|_|\__|_|\_/\___|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/

@instantiate
class anything(condition):
	def evaluate(self, item):
		return True

@instantiate
class nothing(condition):
	def evaluate(self, item):
		return False


class identity(condition):
	identity = RTS.positional()

	def evaluate(self, item):
		return item is identity

class instance_of(condition):
	type = RTS.positional()

	def evaluate(self, item):
		return isinstance(item, self.type)

class subclass_of(condition):
	type = RTS.positional()

	def evaluate(self, item):
		return isinstance(item, type) and issubclass(item, self.type)

class type_identity(condition):
	type = RTS.positional()

	def evaluate(self, item):
		return item.__class__ is self.type

class equal_to(condition):
	value = RTS.positional()

	def evaluate(self, item):
		return item == value


#   ___                                _    ___             _ _ _   _
#  / __|___ _ __  _ __  ___ ___ ___ __| |  / __|___ _ _  __| (_) |_(_)___ _ _  ___
# | (__/ _ \ '  \| '_ \/ _ (_-</ -_) _` | | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
#  \___\___/_|_|_| .__/\___/__/\___\__,_|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/
#                |_|


class any_subcondition(condition):
	sub_conditions = RTS.all_positional()

	def __repr__(self):
		return ' | '.join(repr(b) for b in self.sub_conditions)


	def evaluate(self, item):
		for sc in self.sub_conditions:
			if sc.evaluate(item):
				return True

		return False

class all_subconditions(condition):
	sub_conditions = RTS.all_positional()

	def evaluate(self, item):
		for sc in self.sub_conditions:
			if not sc.evaluate(item):
				return False

		return True

	def __repr__(self):
		return ' & '.join(repr(b) for b in self.sub_conditions)



class function(condition):
	target = RTS.field(default=ANYTHING)
	positional = RTS.field(default=ANYTHING)
	named = RTS.field(default=ANYTHING)
	returns = RTS.field(default=ANYTHING)

