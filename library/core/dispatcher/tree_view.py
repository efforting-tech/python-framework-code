from .. import record as R
from . import Regulations, Dispatcher, Regex_Regulations
from .rules import  Tree_View_Regex_Rule, Node_Classification_Rule
from ..text.tree import Tree_Node_Classification
from ... import Symbol as S
from ..decoration import Pending_Decorator
import re

#NOTE - changed responsibility for .title to not be the tree view dispatcher directly but rather the regulations

class Tree_View_Dispatcher(Dispatcher):
	regulations: R.Field(factory=Regulations)


	def register(self, pattern_factory, *pattern_positionals, **pattern_named):

		def finalize(target):	#TODO - should we do it like this?
			self.regulations.rules.append(pattern_factory(*pattern_positionals, target, **pattern_named))
			return target

		return Pending_Decorator(finalize)

	def register_regex_function(self, pattern, flags=0):
		return self.register(Tree_View_Regex_Rule, re.compile(pattern, flags))

	def register_empty_function(self):
		return self.register(Node_Classification_Rule, {Tree_Node_Classification.Empty})	#TODO - function specifically for node classification?

	def bound_dispatch_tree(self, target, node):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in node.iter_nodes():
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.bound_dispatch_node(target, sub_item))

		return result_aggregator


	def bound_dispatch_node(self, target, node):
		if (match := self.dispatch_item(node)) and match.value != S.Not_Set:
			#Assume function for now
			return match.value.rule.action(target, self, node, match)
		else:
			raise Exception(f'No match for {node!r} in {self!r}')	#TODO - default handler, better message

	def dispatch_tree(self, node):
		result_aggregator = self.sequence_aggregator_type()
		#print('DT', node, tuple(node.iter_nodes()))
		if node:
			if node.classification is Tree_Node_Classification.Empty:
				result_aggregator.aggregate(self.dispatch_node(node))
			else:
				for sub_item in node.iter_nodes():
					if not result_aggregator.accepting_work:
						break

					result_aggregator.aggregate(self.dispatch_node(sub_item))

		return result_aggregator

	def dispatch_node(self, node):
		if (match := self.dispatch_item(node)) and match.value != S.Not_Set:
			#Assume function for now
			return match.value.rule.action(self, node, match)
		else:
			raise Exception(f'No match for {node!r} in {self!r}')	#TODO - default handler, better message


#NOTE: We will probably just add an interface for adding regex functions to the regular dispatcher instead

# class Tree_View_Regex_Dispatcher(Tree_View_Dispatcher):
# 	regulations: R.Field(factory=Regex_Regulations)

# 	def register(self, pattern_factory, *pattern_positionals, **pattern_named):
# 		pattern = pattern_factory(*pattern_positionals, **pattern_named)
# 		def finalize(target):
# 			import re
# 			#TODO - re.compile can be omitted when Record can ensure type
# 			self.regulations.rules.append(Regex_Rule(re.compile(pattern), target))
# 			return target

# 		return Pending_Decorator(finalize)
