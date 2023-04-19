from .. import type_system as RTS
from ..type_system.features import classmethod_with_specified_settings
from ..type_system.bases import public_base
from .. import pattern_matching as PM

#TODO - priority_translator is a more mature version of this - we should harmonize - now there will be some duplication

#TODO - we are providing something similar in "conditional data processing", we should harmonize
#	maybe all data processing things should be under one thing and then the specializations, create nicer structure

import types

class pending_processor_function(public_base):
	processor = RTS.positional()
	condition = RTS.positional()

	def __call__(self, function):
		processor = self.processor
		action = yield_processed_value(types.MethodType(function, processor))	#Bind to processor
		processor.rules += ((self.condition, action),)


class pending_processor_from_class(public_base):
	processor = RTS.positional()

	def __call__(self, cls):
		processor = self.processor
		processor.rules = list(processor.rules)	#Make rules mutable
		for key, function in cls.__dict__.items():
			if callable(function):
				condition = processor.condition_parser(function)
				action = yield_processed_value(types.MethodType(function, processor))	#Bind to processor
				processor.rules.append((condition, action))	#TODO use rule container

		return processor

class generic_processor(public_base):
	#TODO - we may later add features for per item filtering, per item target_type and such but for now we are starting simple
	#NOTE - we change to use list for rules, this may break some invocations - we need to check this
	rules = RTS.positional(factory=list)
	condition_parser = RTS.setting(None)
	post_processor = RTS.setting(tuple)
	context = RTS.setting()
	default_action = RTS.setting(None)

	#TODO - other variations
	def on_type_identity(self, identity):
		return pending_processor_function(self, PM.type_identity(identity))

	def on_identity(self, identity):
		return pending_processor_function(self, PM.identity(identity))


	@classmethod_with_specified_settings(RTS.SELF)
	def from_class_and_settings(cls, config):
		return pending_processor_from_class(cls._from_config(config))

	def process_sequence_iteratively(self, sequence):	#TODO create some nice API for all the process X features throughout the project
		for item in sequence:
			yield self.process_item(item)

	def process_sequence(self, sequence):	#TODO create some nice API for all the process X features throughout the project
		return self.post_processor(self.process_sequence_iteratively(sequence))

	def process_item(self, item):
		for condition, action in self.rules:
			if match := condition.match(item):
				return action.take_action(self, match, item)	#TODO maybe we should support other things than just returning - similar to how other places do this - we should collect them all in one place

		if self.default_action:
			return self.default_action.take_action(self, unconditional_match(item), item)
		else:
			raise Exception(item)


	def add_contextual_conditional_function(self, context, condition, body):

		#(C=processor.context, CX=processor.context.accessor, P=processor, M=match_object (pending), I=node, **M.named)

		args = ', '.join(('C', 'CX', 'P', 'M', 'I'))	#NOTE - we may add M-related stuff here later on if the pattern matching has captures but until then we just do it like this
		function = context.create_function2(body, args)
		self.rules.append((condition, call_function_wpcam(function)))


	def add_contextual_default_function(self, context, body):
		args = ', '.join(('C', 'CX', 'P', 'M', 'I'))
		function = context.create_function2(body, args)
		self.default_action = call_function_wpcam(function)



	__call__ = process_item	#Default operation








class dispatch_action(public_base):
	pass

class yield_processed_value(dispatch_action):
	processor = RTS.positional()

	def take_action(self, processor, match, item):
		return self.processor(item)

class yield_item(dispatch_action):

	def take_action(self, processor, match, item):
		return item


#NOTE - not to be confused with the one in improved_text_node_processor - we really should make a neat namespace for this!
class call_function_wpcam(public_base):	#with_processor_context_and_match
	function = RTS.positional()

	def take_action(self, processor, match, item):

		return self.function(C=processor.context, CX=processor.context.accessor, P=processor, M=match, I=item)
		#Later we will include named captures from match - if there are any
		#	we will use a similar approach as with


class unconditional_match(public_base):
	item = RTS.positional()