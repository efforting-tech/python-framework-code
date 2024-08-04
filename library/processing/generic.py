#TODO - harmonize/inheritance of similar/common
#	process_item should have *additional_positionals and also named
from ..record.base.public import Structure
from ..record import member as M
from .. import symbol, ABC
from .structures import Processor_State, Rule_Set, Pending_LUT_Process_Function, LUT_Rule_Set, Pending_LUT_Compare_Function, Call_Comparator_Function, Call_Processing_Function

class Base_Processor(Structure):
	name = M.positional(default=None)
	rules = M.positional(factory=Rule_Set, repr=False)

class Processor(Base_Processor):
	STATE_TYPE = Processor_State

	def __call__(self, pre_existing_state=None, state=None):
		if pre_existing_state:
			return pre_existing_state.with_processor(self)
		else:
			if state:
				return type(self).STATE_TYPE(self, **state)
			else:
				return type(self).STATE_TYPE(self)

	#def process_node(self, node):
		#print(node.title)



class Iterator(Base_Processor):
	pass

class LUT_Processor(Processor):
	name = M.positional(default=None)
	rules = M.positional(factory=LUT_Rule_Set)

class LUT_Iterator(Iterator):
	name = M.positional(default=None)
	rules = M.positional(factory=LUT_Rule_Set)

	def register(self, action):
		return Pending_LUT_Process_Function(self, action)

	def register_default(self):
		return Pending_LUT_Process_Function(self, symbol.action.default)


class Type_LUT_Iterator(LUT_Iterator):
	def __call__(self, item):
		match self.rules.lookup_action(type(item)):
			case Call_Processing_Function(function):
				return function(self, item)

			case sym if sym is symbol.action.raise_exception:
				raise Exception(f'Failed to process {type(item)!r} in {type(self).__qualname__} {self.name!r}')

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case sym if sym in symbol.action:
				raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {unhandled}')	#TODO - better error



class Type_LUT_Processor(LUT_Processor):

	def process_item(self, item):
		match self.rules.lookup_action(type(item)):
			case Call_Processing_Function(function):
				return function(self, item)

			case sym if sym is symbol.action.raise_exception:
				raise Exception(f'Failed to process {type(item)!r} in {type(self).__qualname__} {self.name!r}')

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case sym if sym in symbol.action:
				raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {unhandled}')	#TODO - better error

	def register(self, action):
		return Pending_LUT_Process_Function(self, action)

	def register_default(self):
		return Pending_LUT_Process_Function(self, symbol.action.default)

class Identity_LUT_Processor(LUT_Processor):

	def process_item(self, item, *additional_positionals):
		match self.rules.lookup_action(item):
			case Call_Processing_Function(function):
				return function(self, item, *additional_positionals)

			case sym if sym is symbol.action.raise_exception:
				raise Exception(f'Failed to process {item!r} in {type(self).__qualname__} {self.name!r}')

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case sym if sym in symbol.action:
				raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {unhandled}')	#TODO - better error

	def register(self, action):
		return Pending_LUT_Process_Function(self, action)

	def register_default(self):
		return Pending_LUT_Process_Function(self, symbol.action.default)


class Type_LUT_Comparator(Type_LUT_Processor):
	def compare_items(self, expected, subject):
		match self.rules.lookup_action(type(expected)):
			case Call_Comparator_Function(function):
				return function(self, expected, subject)

			case sym if sym is symbol.action.raise_exception:
				raise Exception(f'Failed to compare {subject!r} to {expected} in {type(self).__qualname__} {self.name!r}')

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case sym if sym in symbol.action:
				raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {unhandled}')	#TODO - better error


	def register(self, action):
		return Pending_LUT_Compare_Function(self, action)

	def register_default(self):
		return Pending_LUT_Compare_Function(self, symbol.action.default)