from .. import rudimentary_type_system as RTS
from ..rudimentary_type_system.bases import public_base
from ..rudimentary_type_system.features import classmethod_with_specified_settings, method_with_specified_settings
from ..rudimentary_features.code_manipulation.templating.pp_context import context
from ..table_processing.table import table
from .improved_tokenization import simple_priority_translator, regex_parser
from ..text_processing.re_match_processing import match_iterator

import sys

def expect_one(gen):
	[item] = gen
	return item

#TODO the parse_text_node_processor_action should probably be improved a bit. Maybe create APIs that are useful no matter if we are using text_node or table or whatever we may be doing

class A:
	class return_expression(public_base):
		expression = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return processor.context.eval_expression_dict(self.expression, dict(C=processor.context, P=processor, M=M, N=node, **M.named))

parse_text_node_processor_action = simple_priority_translator.from_raster(r'''

	pattern							expression
	-------							----------
	return {expression}				A.return_expression(M.pending_positional)

''', pattern_processor=regex_parser, post_processor=expect_one, context=context.from_this_frame()).process_text



class improved_text_node_processor(public_base):
	rules = RTS.all_positional(field_type=RTS.SETTING)
	context = RTS.setting(factory=context.from_frame, factory_positionals=(sys._getframe(0),), factory_named=dict(update_linecache=True))
	pattern_processor = RTS.setting()
	action_processor = RTS.setting(parse_text_node_processor_action)
	post_processor = RTS.setting(tuple)

	@classmethod_with_specified_settings(RTS.SELF)
	def from_raster(cls, raster_table, config):
		#rules = config._target.pop('rules', None) or ()	#TODO - this is a big of an ugly hack
		instance = cls._from_state(config._resolve())

		rules = list()
		pattern_processor = config.pattern_processor
		action_processor = config.action_processor

		#PME = types.MethodType(cls.process_matched_expression, instance)

		for pattern, action in table.from_raster(raster_table).strict_iter('pattern', 'action'):
			re_pattern = pattern_processor(pattern)
			parsed_action = action_processor(action)
			rules.append((re_pattern, parsed_action))

		instance.rules += tuple(rules)

		return instance

	#def process_matched_expression(self, match, context, expression):
		#assert expression, f'Encountered empty expression when evaluating match {match} using {self.tokenizer}'
		#return context.eval_expression_dict(expression, dict(processor=self, node, **match.groupdict()))

	def process_node(self, node):
		for pattern, action in self.rules:
			if match := pattern.match(node.title):
				return action.take_action(self, node, match)

		else:
			raise Exception(node.title)

	def process_tree_iteratively(self, tree):
		for node in tree.iter_nodes():
			yield self.process_node(node)

	def process_tree(self, tree):
		return self.post_processor(self.process_tree_iteratively(tree))



