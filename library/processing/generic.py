from ..processing.dispatcher import Named_Dispatcher, LUT_Regulations, generic_data_condition, unconditional_rule, Type_LUT_Regulations, regex_rule, Regulations
from .stack import Stack, Stack_Frame
from ..record import member as M
from ..record.base.public import Structure
from .. import ABC, symbol
from .structures import Call_Processing_Function


import re


@ABC.Decorator
class Pending_LUT_Processor_Function(Structure):
	owner = M.positional()
	condition = M.positional()

	def __call__(self, function):
		#self.owner.map_action(self.action, Call_Processing_Function(function))
		#self.owner.regulations.rules[] = generic_data_condition(DC.Identity(token), action)

		self.owner.regulations.rules[self.condition] = Call_Processing_Function(function)

		return function

@ABC.Decorator
class Pending_Regex_Processor_Function(Structure):
	owner = M.positional()
	pattern = M.positional()

	def __call__(self, function):
		self.owner.regulations.rules.append(regex_rule(re.compile(self.pattern), Call_Processing_Function(function)))
		return function

class Processor(Named_Dispatcher):
	regulations = M.positional(factory=Regulations)

	match = M.positional(factory=Stack)
	item = M.positional(factory=Stack)


	def process_item(self, item, *additional_positionals):
		#NOTE The additional_positionals can be fairly neat but currently action processing is duplicated
		#TODO Revise how we register actions with positionals
		match = self.dispatch_item(item)

		with Stack_Frame(self.match, match, self.item, item):
			assert match, f'No match for {item!r}'	#TODO better
			action = match.value.rule.action

			match action:
				case Call_Processing_Function(function):
					return function(self, item, *additional_positionals)

				case sym if sym is symbol.action.raise_exception:
					raise Exception(f'Failed to process {type(item)!r} in {type(self).__qualname__} {self.name!r}')

				case ABC.Action() as action:
					raise Exception(f'Unsupported action: {action}')	#TODO - better error

				case sym if sym in symbol.action:
					raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

				case unhandled:
					raise Exception(f'Unknown action: {unhandled}')	#TODO - better error


class LUT_Processor(Processor):
	regulations = M.positional(factory=LUT_Regulations)

	def register(self, condition):
		return Pending_LUT_Processor_Function(self, condition)

	def register_default(self):
		return Pending_LUT_Processor_Function(self, symbol.action.default)



class Type_LUT_Processor(LUT_Processor):
	regulations = M.positional(factory=Type_LUT_Regulations)


class Identity_LUT_Processor(LUT_Processor):
	pass

class Regex_Processor(Processor):

	def register(self, action):
		return Pending_Regex_Processor_Function(self, action)

	def register_default(self):
		return Pending_Regex_Processor_Function(self, symbol.action.default)




if False:

	#TODO - deprecated - rewrite for dispatcher system

	#TODO - harmonize/inheritance of similar/common
	#	process_item should have *additional_positionals and also named
	from ..record.base.public import Structure
	from .. import symbol, ABC
	from .structures import Regex_Processor_State, Processor_State, Rule_Set, Pending_LUT_Process_Function, LUT_Rule_Set, Pending_LUT_Compare_Function, Call_Comparator_Function, Call_Processing_Function, Pending_Process_Function, Regex_Rule_Set

	class Base_Processor(Structure):
		name = M.positional(default=None)
		rules = M.positional(factory=Rule_Set, repr=False)
		STATE_TYPE = M.positional(default=None)

	class Processor(Base_Processor):
		STATE_TYPE = M.positional(default=Processor_State)

		def __call__(self, pre_existing_state=None, state=None):
			if pre_existing_state:
				return pre_existing_state.with_processor(self)
			else:
				if state:
					return self.STATE_TYPE(self, **state)
				else:
					return self.STATE_TYPE(self)

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

		def process_item(self, item, *additional_positionals):	#TODO - should we have additiona_positionals or not?
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
			#TODO - we should probably separate the take action part from the look up action part to prevent code duplication
			#TODO - we should also have support for having a different expected for decision than for calling function, like we do with branchable_iterator for the mnemonic_comparator
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


	class Regex_Processor(Processor):
		rules = M.positional(factory=Regex_Rule_Set)
		STATE_TYPE = M.positional(default=Regex_Processor_State)

		def process_item(self, item, *additional_positionals):	#TODO - should we have additiona_positionals or not?
			self.rule, self.match = self.rules.lookup_rule_and_match(item)	#TODO - here we are assuming processor_state for self - we may want to refine this
			match self.rule.action:
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
			return Pending_Process_Function(self, action)

		def register_default(self):
			return Pending_Process_Function(self, symbol.action.default)

