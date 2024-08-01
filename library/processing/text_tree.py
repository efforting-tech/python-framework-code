from .. import ABC
from ..matching import data_condition as DC
from ..mnemonic_language.parser import tp
from ..mnemonic_language.parsing_rules import element_comparator
from ..record import member as M
from ..record.base.public import Structure
from .generic import Processor
from .structures import Rule_Set, Call_Text_Tree_Processing_Function, Processor_State

#TODO - we should rethink a bit how we deal with our states, it is a bit messy for now, especially with the __getattr__ pattern. That is not nice, introspectable or anything.
#		it should probably be more that we have specific methods in the state that is aware of how to access the specific processor
#		We can possibly avoid code duplication with some nifty common interfaces



class Text_Tree_Processor_State(Processor_State):
	node = M.state(None)
	rule = M.state(None)

	def process_tree(self, tree):
		for node in tree.iter_nodes():
			self.node = node
			if self.title_processor:
				title_subject = self.title_processor(node.title)
			else:
				title_subject = node.title

			for rule in self.rules:
				self.rule = rule
				#We are assuming that the rules are of DC.Mnemonic but we should check it, possibly when adding the rules. TODO - type checking for valid rules in Rule_Set classes?
				if self.title_comparator(self).compare_items(rule.condition.value, title_subject):	#We use self here when calling title comparator so that it will use our own captures dict

					match rule.action:
						case Call_Text_Tree_Processing_Function(function):
							return function(self)

						#TODO - check uncommented

						# case sym if sym is symbol.action.raise_exception:
						# 	raise Exception(f'Failed to process {type(item)!r} in {type(self).__qualname__} {self.name!r}')

						# case ABC.Action() as action:
						# 	raise Exception(f'Unsupported action: {action}')	#TODO - better error

						# case sym if sym in symbol.action:
						# 	raise Exception(f'Unsupported action symbol: {sym}')	#TODO - better error

						case unhandled:
							raise Exception(f'Unknown action: {unhandled}')	#TODO - better error



@ABC.Decorator
class Pending_Text_Tree_Process_Function(Structure):
	owner = M.positional()
	condition = M.positional()

	def __call__(self, function):
		self.owner.add_conditional_action(self.condition, Call_Text_Tree_Processing_Function(function))
		return function


class Text_Tree_Rule_Set(Rule_Set):
	def register_mnemonic(self, mnemonic):
		if isinstance(mnemonic, str):
			return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(tp.process_text(mnemonic)))
		else:
			return Pending_Text_Tree_Process_Function(self, DC.Mnemonic(mnemonic))




class Text_Tree_Processor(Processor):
	STATE_TYPE = Text_Tree_Processor_State
	rules = M.positional(factory=Text_Tree_Rule_Set, repr=False)	#TODO - maybe we should have a specific type for when we are replacing an existing member? Or maybe this is fine. To be discussed/determined
	title_comparator = M.positional(None)
	title_processor = M.positional(None)

	def process_tree(self, tree):
		raise NotImplementedError('stateless process_tree')



class Mnemonic_Text_Tree_Processor(Text_Tree_Processor):
	title_comparator = M.positional(element_comparator)
	title_processor = M.positional(tp.process_text)
