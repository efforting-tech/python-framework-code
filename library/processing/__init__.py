from ..record.base.public import Structure
from ..record import member as M
from .. import symbol

#TODO - harmonize/inheritance of similar/common


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
			raise Exception()	#TODO - proper exception
		elif isinstance(pending, LUT_Rule):
			return pending.action
		else:
			return self.default_action or default

class Processor(Structure):
	name = M.positional(default=None)
	rules = M.positional(factory=Rule_Set, repr=False)

	def process_node(self, node):
		print(node.title)

class LUT_Processor(Structure):
	name = M.positional(default=None)
	rules = M.positional(factory=LUT_Rule_Set)

	def process_node(self, node):
		print(node.title)