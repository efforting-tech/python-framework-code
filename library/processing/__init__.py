from ..record.base.public import Structure
from ..record import member as M
from .. import symbol, ABC

#TODO - harmonize/inheritance of similar/common

#TODO - Move actions?
@ABC.Action
class Call_Comparator_Function(Structure):
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
	fallback = M.positional(None)


	def map_action(self, value=None, action=None):
		self.rules[value] = LUT_Rule(value, action)


	def lookup_action(self, value, default=symbol.raise_exception):
		pending = self.rules.get(value, default)

		if pending is symbol.raise_exception:
			raise Exception(value)	#TODO - proper exception
		elif isinstance(pending, LUT_Rule):
			return pending.action
		else:
			return self.default_action or default

class Processor(Structure):
	name = M.positional(default=None)
	rules = M.positional(factory=Rule_Set, repr=False)

	#def process_node(self, node):
		#print(node.title)

class LUT_Processor(Structure):
	name = M.positional(default=None)
	rules = M.positional(factory=LUT_Rule_Set)

	#def process_node(self, node):
		#print(node.title)

class Type_LUT_Processor(LUT_Processor):
	pass

@ABC.Decorator
class Pending_LUT_Comparator_Function(Structure):
	owner = M.positional()
	action = M.positional()

	def __call__(self, function):
		self.owner.rules.map_action(self.action, Call_Comparator_Function(function))
		return function

class Type_LUT_Comparator(Type_LUT_Processor):

	def compare_items(self, expected, subject):
		match self.rules.lookup_action(type(expected)):
			case Call_Comparator_Function(function):
				return function(self, expected, subject)

			case ABC.Action() as action:
				raise Exception(f'Unsupported action: {action}')	#TODO - better error

			case unhandled:
				raise Exception(f'Unknown action: {action}')	#TODO - better error


	def register(self, action):
		return Pending_LUT_Comparator_Function(self, action)