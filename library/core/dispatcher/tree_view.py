from .. import record as R
from . import Regulations, Dispatcher
from .rules import Regex_Rule

class Tree_View_Dispatcher(Dispatcher):
	regulations: R.Field(factory=Regulations)


	def register(self, pattern_factory, *pattern_positionals, **pattern_named):
		pattern = pattern_factory(*pattern_positionals, **pattern_named)
		def finalize(target):
			import re
			#TODO - re.compile can be omitted when Record can ensure type
			self.regulations.rules.append(Regex_Rule(re.compile(pattern), target))
			return target

		return pending_decorator(finalize)



	def bound_dispatch_tree(self, target, node):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in node.iter_nodes():
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.bound_dispatch_node(target, sub_item))

		return result_aggregator


	def bound_dispatch_node(self, target, node):
		if match := self.dispatch_item(node.title):
			#Assume function for now
			return match.value.rule.action(target, self, node, match)
		else:
			raise Exception(f'No match for {node.title!r} in {self!r}')	#TODO - default handler, better message

	def dispatch_tree(self, node):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in node.iter_nodes():
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.dispatch_node(sub_item))

		return result_aggregator


	def dispatch_node(self, node):
		if match := self.dispatch_item(node.title):
			#Assume function for now
			return match.value.rule.action(self, node, match)
		else:
			raise Exception(f'No match for {node.title!r} in {self!r}')	#TODO - default handler, better message

class pending_decorator:
	def __init__(self, finalizer):
		self.finalizer = finalizer

	def __call__(self, target):
		return self.finalizer(target)


