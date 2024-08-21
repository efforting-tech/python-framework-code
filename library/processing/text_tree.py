from .. import symbol
from ..record import member as M
from ..record.base.public import Structure, Sequence
from .dispatcher import Dispatcher
from .generic import Processor
from .stack import Stack, Stack_Frame

#TODO - project wide - ABC and also check for location of definitions that may be in the wrong place





class Text_Tree_Dispatcher_Action(Structure):
	target = M.positional()


class Text_Tree_Dispatcher(Processor):
	#title_preprocessor = M.positional(None)
	tree = M.positional(factory=Stack)
	node = M.positional(factory=Stack)
	title = M.positional(factory=Stack)

	def process_action(self, rule_match):
		action = rule_match.rule.action

		if action is symbol.action.skip:
			return action
		elif action is symbol.action.sub_dispatcher:
			return type(rule_match.rule.dispatcher).process_action(self, rule_match.match.value)	#TODO should we use the type of the dispatcher or should we just use our own process_action?

		match action:
			case Text_Tree_Dispatcher_Action(target):
				return target(self)

			case unhandled:
				raise Exception(unhandled)#TODO better

	def dispatch_node(self, node):
		title = node.title
		#if self.title_preprocessor:
		#	title = self.title_preprocessor(title)

		if match := self.dispatch_item(title):
			with Stack_Frame(self.node, node, self.title, title, self.match, match):
				return self.process_action(match.value)
		else:
			raise Exception(f'No match for {title!r}')	#TODO - default handler, better message


	def dispatch_tree(self, tree):
		result = self.sequence_aggregator_type()
		with Stack_Frame(self.tree, tree):
			for node in tree.iter_nodes():
				result.aggregate(self.dispatch_node(node))

		return result



if False:
	#TODO - deprecated - rewrite with new dispatching system

	from .. import ABC
	from ..matching import data_condition as DC
	#from ..mnemonic_language.parser import tp	#TODO - this should not be coupled from within text_tree, text_tree should be used to build mnemonic_tree
	#from ..mnemonic_language.parsing_rules import mnemonic_comparator
	from ..record import member as M
	from ..record.base.public import Structure
	from .generic import Processor
	from .structures import Rule_Set, Call_Text_Tree_Processing_Function, Processor_State

	#TODO - maybe we should not have title comparator but instead make sure the processing/rule framework is better structured - it would be great though if we could create processors from parameters instead of hard coding all kinds of very similar ones

	#TODO - we should rethink a bit how we deal with our states, it is a bit messy for now, especially with the __getattr__ pattern. That is not nice, introspectable or anything.
	#		it should probably be more that we have specific methods in the state that is aware of how to access the specific processor
	#		We can possibly avoid code duplication with some nifty common interfaces


	#TODO - lots of these utility functions should have fallbacks so that they'll work even during early errors
	#		for now we will just assume that we only use this for mnemonics #UGLY-HACK
	def get_string_representation(item):
		try:
			from ..mnemonic_language.string_formatting_rules import string_formatter
			return repr(string_formatter.process_item(item))
		except:
			return repr(item)

	class Text_Tree_Processor_State(Processor_State):
		node = M.state(None)
		item = M.state(None)
		rule = M.state(None)
		context = M.state(None)
		tracker = M.state(None)
		result_stack = M.state(factory=list)

		def with_processor(self, processor):
			#TODO - use some copy protocol?
			result = type(self)(processor=processor, captures=self.captures, capture_meta=self.capture_meta, node=self.node, item=self.item, rule=self.rule, context=self.context, tracker=self.tracker, result_stack=self.result_stack)
			return result

		def process_action(self, action):
			match action:
				case Call_Text_Tree_Processing_Function(function):
					result = function(self)
					if self.result_stack:
						self.result_stack[-1].append(result)

					return result

				#TODO - check uncommented

				# case sym if sym is symbol.action.raise_exception:
				# 	raise Exception(f'Failed to process {type(item)!r} in {type(self).__qualname__} {self.name!r}')

				# case ABC.Action() as action:
				# 	raise Exception(f'Unsupported action: {action}')	#TODO - better error

				# case sym if sym in symbol.action:
				# 	raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

				case unhandled:
					raise Exception(f'Unknown action: {unhandled}')	#TODO - better error

		def process_item(self, title_subject):
			#TODO - we should use the rulesystem API to get the correct rule instead (but we need to harmonize our processors and make sure we can build up all the different kinds)
			self.item = title_subject
			for rule in self.rules:
				self.rule = rule
				#We are assuming that the rules are of DC.Mnemonic but we should check it, possibly when adding the rules. TODO - type checking for valid rules in Rule_Set classes?
				if self.with_processor(self.title_comparator).compare_items(rule.condition.value, title_subject):
					return self.process_action(rule.action)


			raise Exception(f'Failed to handle: {get_string_representation(title_subject)}')	#TODO - better error


		def process_node(self, node):
			self.captures.clear()	#TODO - is there any case where we don't want to do this?
			self.node = node
			if self.title_processor:
				return self.process_item(self.title_processor(node.title))
			else:
				return self.process_item(node.title)

		def process_tree(self, tree):
			self.result_stack.append(list())
			for node in tree.iter_nodes():
				self.process_node(node)

			return self.result_stack.pop()



	@ABC.Decorator
	class Pending_Text_Tree_Process_Function(Structure):
		owner = M.positional()
		condition = M.positional()

		def __call__(self, function):
			self.owner.rules.add_conditional_action(self.condition, Call_Text_Tree_Processing_Function(function))
			return function


	# class Text_Tree_Rule_Set(Rule_Set):
	# 	def register_mnemonic(self, mnemonic):
	# 		if isinstance(mnemonic, str):
	# 			return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(tp.process_text(mnemonic)))
	# 		else:
	# 			return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(mnemonic))




	class Text_Tree_Processor(Processor):
		STATE_TYPE = M.positional(default=Text_Tree_Processor_State)
		#rules = M.positional(factory=Text_Tree_Rule_Set, repr=False)	#TODO - maybe we should have a specific type for when we are replacing an existing member? Or maybe this is fine. To be discussed/determined
		title_comparator = M.positional(None)
		title_processor = M.positional(None)

		def process_tree(self, tree):
			raise NotImplementedError('stateless process_tree')

		def register(self, mnemonic):
			if isinstance(mnemonic, str):
				from ..mnemonic_language.mnemonic_tokens_to_pattern import mttp
				return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(mttp.process_item(tp.process_text(mnemonic))))		#TODO - maybe we should clean this up a bit and not involve the DC stuff here?
			else:
				return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(mnemonic))


