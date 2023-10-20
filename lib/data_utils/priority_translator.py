#from ..symbols import create_symbol
from ..type_system.bases import public_base
from .. import type_system as RTS	#TODO - all RTS refs should be turned to TS
from .. import pattern_matching as PM	#TODO - conditions as C?
from ..improved_mnemonic_tree_processor import actions as A
from ..improved_mnemonic_tree_processor import matches as M
from ..improved_mnemonic_tree_processor.tree_node_processing import call_bound_function_with_configuration_and_item
from ..improved_mnemonic_tree_processor.context import context
from ..type_system.features import method_with_specified_settings
from ..data_utils import identity_reference
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
	context = RTS.setting(factory=context.from_this_frame, factory_positionals=(3,), factory_named=dict(name='default_context'))	#Why 3? Will it change? Is this a terrible practice?


	def add_rule(self, condition, action):
		self.rules.append(conditional_action(condition, action))

	@method_with_specified_settings(RTS.SELF)
	def process_sequence(self, sequence, *, config):
		return tuple(self.process_item.call_with_config(config, item) for item in sequence)

	@method_with_specified_settings(RTS.SELF)
	def process_item(self, item, *, config):

		def take_action(action, match):
			match action:
				case return_value(value):
					return value

				case A.bind_and_call_function_with_processor_config_and_item(function):
					return call_bound_function_with_configuration_and_item(function.__get__(self, self.__class__), (config,), match)	#TODO - we should return a proper match object but we are using the wrong conditions here

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		for rule in self.rules:
			if match := rule.condition.check_match(item):
				return take_action(rule.action, match)

		if self.default_action:
			return take_action(self.default_action, M.matched_unconditionally(item))
		else:
			raise Exception(f'Could not handle: {item!r}')


	#DEPRECATED
	# def process_item(self, item):
	# 	for rule in self.rules:	#TODO - we should harmonize all the rule systems and perhaps also use a rule type for the rules rather than tuple of cond/act, we should also harmonize take_action_for_item, perhaps to (processor, rule, match, item)
	# 		if match := rule.condition.match(item):
	# 			return rule.action.take_action_for_item(self, rule, match, item)

	# 	if self.default_action:
	# 		self.default_action.take_action_for_item(self, None, unconditional_match(item), item)

	# 	else:
	# 		raise Exception(item)

	#TODO def extend(...)

	# def add_conditional_action(self, condition, action):
	# 	self.rules.append(conditional_action(condition, action))


	# #TODO - other variations
	# def on_type_identity(self, identity):
	# 	return pending_conditional_item_processor(self, PM.type_identity(identity))

	# def bound_on_type_identity(self, identity):
	# 	return pending_conditional_bound_item_processor(self, PM.type_identity(identity))

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
			if match := rule.condition.check_match(item):
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

class circular_graph_tolerant_priority_translator(priority_translator):
	cache = RTS.state(factory=dict)
	finalize_item_cache = RTS.state(None)
	#NOTE - must provide cache_item

	@method_with_specified_settings(RTS.SELF)
	def process_item(self, item, *, config):
		idref = identity_reference(item)
		if cached := self.cache.get(idref):
			return cached

		self.cache[idref] = self.prepare_item_cache(idref)
		result = super().process_item.call_with_config(config, item)
		if self.finalize_item_cache:
			self.cache[idref] = self.finalize_item_cache(idref, result)
		return result


