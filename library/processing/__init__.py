from ..record.base.public import Structure
from ..record import member as M
from .. import symbol, ABC

#TODO - put more ABC in here

#TODO - harmonize/inheritance of similar/common

#TODO - Move actions?
@ABC.Action
class Call_Comparator_Function(Structure):
	function = M.positional()

@ABC.Action
class Call_Processing_Function(Structure):
	function = M.positional()



class Rule(Structure):
	condition = M.positional(None)
	action = M.positional(None)

class LUT_Rule(Structure):
	value = M.positional(None)
	action = M.positional(None)

class Rule_Set(Structure):
	rules = M.positional(factory=list, repr=False)
	fallback = M.positional(None)

	def add_conditional_action(self, condition=None, action=None):
		self.rules.append(Rule(condition, action))

class LUT_Rule_Set(Structure):
	rules = M.positional(factory=dict, repr=False)
	default_action = M.positional(None)
	fallback = M.positional(None)	#TODO - support??


	def map_action(self, value=None, action=None):
		if value is symbol.action.default:
			self.default_action = action
		else:
			self.rules[value] = LUT_Rule(value, action)


	def lookup_action(self, value, default=symbol.action.raise_exception):
		MISS = object()	#TODO - local symbol
		pending = self.rules.get(value, MISS)

		if pending is MISS:
			return self.default_action or default
			#TODO - support fallback??

		if pending is symbol.action.raise_exception:
			raise Exception(value)	#TODO - proper exception
		elif isinstance(pending, LUT_Rule):
			return pending.action
		else:
			return self.default_action or default

class Processor_State(Structure):
	processor = M.positional()
	captures = M.positional(factory=dict)

	#TODO - other API - should we also split them up depending on processor/comparator?
	def compare_items(self, expected, subject):
		return type(self.processor).compare_items(self, expected, subject)

	def store_capture(self, value, name):
		self.captures[name] = value

	def with_processor(self, processor):
		return Processor_State(processor, self.captures)

	def __getattr__(self, name):
		return getattr(self.processor, name)

class Processor(Structure):
	STATE_TYPE = Processor_State
	name = M.positional(default=None)
	rules = M.positional(factory=Rule_Set, repr=False)

	def __call__(self, pre_existing_state=None):
		if pre_existing_state:
			return pre_existing_state.with_processor(self)
		else:
			return type(self).STATE_TYPE(self)

	#def process_node(self, node):
		#print(node.title)

class LUT_Processor(Processor):
	name = M.positional(default=None)
	rules = M.positional(factory=LUT_Rule_Set)

	#def process_node(self, node):
		#print(node.title)

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

@ABC.Decorator
class Pending_LUT_Compare_Function(Structure):
	owner = M.positional()
	action = M.positional()

	def __call__(self, function):
		self.owner.rules.map_action(self.action, Call_Comparator_Function(function))
		return function

@ABC.Decorator
class Pending_LUT_Process_Function(Structure):
	owner = M.positional()
	action = M.positional()

	def __call__(self, function):
		self.owner.rules.map_action(self.action, Call_Processing_Function(function))
		return function



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