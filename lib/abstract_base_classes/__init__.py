#Primitive Decorator - note, we may have a better way to declare decorators later but probably not before abc is initialized

import types
from ..symbols import symbol_node, symbol_attribute_access_interface
from ..exceptions import DataConversionFailed
from ..function_utils.orchestration import call_sequence
from ..data_utils.proxy import proxy_resolve
from collections import defaultdict

from .. import type_system as RTS
from ..type_system.bases import public_base


#TODO - define a project wide representation specification
#	update - I don't actually remember what I meant here, possibly a way to specify formats for __repr__ implementation?
#	TO-DECIDE

#NOTE - we made this a type so that one could use these types in pattern matching as per https://peps.python.org/pep-0634/#class-patterns
#		it is not enough to simply provide __instancecheck__ for match to work properly, it has to actually derive from type.
#TODO - turn this #NOTE into something referencing our documentation once we have that. (see tagging-plans for further information)
class abc_tree_node(symbol_attribute_access_interface, type):
	#EXAMPLE - this is a good example of how we use the symbol_attribute_access_interface and we should have this in the documentation

	def __new__(cls, target):
		return super().__new__(cls, target.name, (), {})

	def __repr__(self):
		return f'<{self._target.path}>'

	def __instancecheck__(self, other):
		#TO DOCUMENT explain proxyresolve
		entry = ABC_DIRECTORY[self]
		if isinstance(proxy_resolve(other), entry.specific_types):
			return True
		else:
			for condition in entry.conditions:
				if condition(other):
					return True
			return False

	def __subclasscheck__(self, other):
		#TO DOCUMENT explain proxyresolve
		entry = ABC_DIRECTORY[self]
		if issubclass(proxy_resolve(other), entry.specific_types):
			return True
		else:
			for condition in entry.subclass_conditions:
				if condition(other):
					return True
			return False

	#TO DECIDE - do we want this for the data conversion feature? Should we define an API for it? We must define the feature data conversion (feature DC)
	def _auto_convert(self, value):
		if isinstance(value, self):
			return value
		else:
			return self._convert(value)

	def _convert(self, value):
		entry = ABC_DIRECTORY[self]
		for from_base, function in entry.auto_conversions:
			if isinstance(proxy_resolve(value), from_base):
				return function(value)

		raise DataConversionFailed(entry, value)



#TO PONDER
#Here it would be nice with the strict binary mapping but since abc is very early in the chain we are going to contend with a unidirectional symbol → abc_metadata mapping for now
#	later we may have a synthetic base type repository we can use for early "advanced" features
class abc_metadata(public_base):
	symbol = RTS.positional()
	conditions = RTS.factory(tuple)
	subclass_conditions = RTS.factory(tuple)	#TODO - implement this
	#TO-DECIDE - do we want to store specific_types in some different way or is tuple fine?
	specific_types = RTS.factory(tuple)	#we need tuple when calling isinstance but set would make more sense otherwise
	auto_conversions = RTS.factory(list)

	#ADD list for auto translation
	#TO PONDER - was this list associated with feature DC? Figure this out.



#TO DOCUMENT - explain the relationship between symbol_node, dict and abc_tree_node
ABC_TREE = symbol_node(name='abc')
ABC_DIRECTORY = dict()
abc = abc_tree_node(ABC_TREE)

class generic_abc_registrator:
	def __init__(self, *path_list):
		self.path_list = set(path_list)

class abc_registrator_used_with_subclass_init(generic_abc_registrator):
	#Note - this one is different because it is used in __init_subclass__
	#TODO - make a wrapper that filters the arguments and use that with the regular abc_registrator and get rid of the base generic_abc_registrator
	def __call__(self, target, **type_options):
		for symbol in register_or_resolve_abstract_base_classes(*self.path_list):
			entry = ABC_DIRECTORY[symbol]
			entry.specific_types += (target,)

class abc_registrator(generic_abc_registrator):
	def __call__(self, target):
		for symbol in register_or_resolve_abstract_base_classes(*self.path_list):
			entry = ABC_DIRECTORY[symbol]
			entry.specific_types += (target,)

class pending_abc_registration:
	def __init__(self, *path_list):
		self.path_list = path_list

class pending_specific_class_registration(pending_abc_registration):
	def __call__(self, target):
		abc_registrator(*self.path_list)(target)
		return target

class pending_class_tree_registration(pending_abc_registration):
	def __call__(self, target):
		scr = abc_registrator_used_with_subclass_init(*self.path_list)

		for path in self.path_list:

			target_func = getattr(target.__init_subclass__, '__func__', None)

			if isinstance(target.__init_subclass__, types.BuiltinFunctionType):
				target.__init_subclass__ = classmethod(scr)
			elif target_func is scr:
				pass #Already hooked into this particular one
			elif isinstance(target_func, generic_abc_registrator):
				target.__init_subclass__ = classmethod(abc_registrator_used_with_subclass_init(*self.path_list, *target_func.path_list))
			elif target_func:
				target.__init_subclass__ = classmethod(call_sequence(scr, target_func))
			else:
				raise Exception(target)

		scr(target)

		return target

#TODO - it would be nice if we could annotate our decorators somehow so that it is clear what their purpose are, maybe we could use a decorator for that.
#Decorator
def register_class_tree(*path_list):
	return pending_class_tree_registration(*path_list)

#Decorator
def register_specific_class(*path_list):
	return pending_specific_class_registration(*path_list)


def register_condition(path, condition):
	[symbol] = register_or_resolve_abstract_base_classes(path)
	meta = ABC_DIRECTORY[symbol]
	meta.conditions += (condition,)
	return symbol

#TODO - this seem to be associated with feature DC - we need to fully map how DC should work.
def register_conversion(path, type, function):
	[symbol] = register_or_resolve_abstract_base_classes(path)
	meta = ABC_DIRECTORY[symbol]
	meta.auto_conversions.append((type, function))
	return symbol

def require_symbol(target):
	if isinstance(target, (abc_tree_node, symbol_node)):
		return target._target
	else:
		return ABC_TREE.require_symbol(target)



def discard_abstract_base_classes(*target_list):
	for target in target_list:
		resolved_target = require_symbol(target)
		del ABC_DIRECTORY[resolved_target]

def register_or_resolve_abstract_base_classes(*name_list):
	result = list()
	for name in name_list:
		symbol = abc_tree_node(ABC_TREE.create_symbol(name))
		if symbol not in ABC_DIRECTORY:
			ABC_DIRECTORY[symbol] = abc_metadata(symbol)
		result.append(symbol)

	return result

def register_abstract_base_classes(*name_list):
	result = list()
	for name in name_list:
		symbol = abc_tree_node(ABC_TREE.create_symbol(name))
		assert symbol not in ABC_DIRECTORY
		ABC_DIRECTORY[symbol] = abc_metadata(symbol)
		result.append(symbol)

	return result