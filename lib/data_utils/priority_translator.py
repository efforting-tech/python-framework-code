#from ..symbols import create_symbol
from ..type_system.bases import public_base
from .. import type_system as RTS	#TODO - all RTS refs should be turned to TS
from .. import pattern_matching as PM	#TODO - conditions as C?
import types

#NOTE - one can use return_value for specific actions such as SKIP, ABORT
#		to really return such a value one can wrap it in something and we probably will have some sort of literal_value() type for this explicit purpose

class unconditional_match(public_base):
	item = RTS.positional()


class conditional_action(public_base):
	condition = RTS.positional()
	action = RTS.positional()

class action(public_base, abstract=True):
	pass

class return_processor(action):
	def take_action_for_item(self, processor, rule, match, item):
		return processor

class return_rule(action):
	def take_action_for_item(self, processor, rule, match, item):
		return rule

class return_match(action):
	def take_action_for_item(self, processor, rule, match, item):
		return match

class return_item(action):
	def take_action_for_item(self, processor, rule, match, item):
		return item

class return_filtered_item(action):
	filter = RTS.positional()
	default = RTS.field(default=None)

	def take_action_for_item(self, processor, rule, match, item):
		return item if self.filter(item) else self.default

class return_processed_item(action):
	processor = RTS.positional()

	def take_action_for_item(self, processor, rule, match, item):
		return self.processor(item)

class return_value(action):
	value = RTS.positional()

	def take_action_for_item(self, processor, rule, match, item):
		return self.value

class priority_translator(public_base):
	rules = RTS.field(factory=list)
	default_action = RTS.field(default=None)

	def process_item(self, item):
		for rule in self.rules:	#TODO - we should harmonize all the rule systems and perhaps also use a rule type for the rules rather than tuple of cond/act, we should also harmonize take_action_for_item, perhaps to (processor, rule, match, item)
			if match := rule.condition.match(item):
				return rule.action.take_action_for_item(self, rule, match, item)

		if self.default_action:
			self.default_action.take_action_for_item(self, None, unconditional_match(item), item)

		else:
			raise Exception(item)

	#TODO def extend(...)

	def add_conditional_action(self, condition, action):
		self.rules.append(conditional_action(condition, action))


	#TODO - other variations
	def on_type_identity(self, identity):
		return pending_conditional_item_processor(self, PM.type_identity(identity))

	def bound_on_type_identity(self, identity):
		return pending_conditional_bound_item_processor(self, PM.type_identity(identity))

class priority_translator_with_context(priority_translator):
	context = RTS.positional()


class collecting_translator(priority_translator):
	post_processor = RTS.field(default=None)

	def process_item(self, item):
		result = list()

		def process_subresult(sub_result):
			if sub_result is SKIP:
				pass
			else:
				result.append(sub_result)


		for rule in self.rules:	#TODO - we should harmonize all the rule systems and perhaps also use a rule type for the rules rather than tuple of cond/act, we should also harmonize take_action_for_item, perhaps to (processor, rule, match, item)
			if match := rule.condition.match(item):
				process_subresult(rule.action.take_action_for_item(self, rule, match, item))

		if self.default_action:
			process_subresult(self.default_action.take_action_for_item(self, None, unconditional_match(item), item))

		else:
			raise Exception(item)

		if self.post_processor:
			return self.post_processor(result)
		else:
			return result

class pending_conditional_item_processor(public_base):
	processor = RTS.positional()
	condition = RTS.positional()

	def __call__(self, function):
		self.processor.add_conditional_action(self.condition, return_processed_item(function))
		return function

class pending_conditional_bound_item_processor(pending_conditional_item_processor):

	def __call__(self, function):
		self.processor.add_conditional_action(self.condition, return_processed_item(types.MethodType(function, self.processor)))
		return function

