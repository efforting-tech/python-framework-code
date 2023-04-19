from .. import type_system as RTS
from ..type_system.bases import public_base
from ..type_system.features import classmethod_with_specified_settings, method_with_specified_settings
from ..rudimentary_features.code_manipulation.templating.pp_context import context
from ..table_processing.table import table
from .improved_tokenization import simple_priority_translator, regex_parser
from ..text_processing.re_match_processing import match_iterator
from ..text_processing.re_tokenization import unconditional_match
from ..text_nodes import text_node
from ..iteration_utils import single_item

import sys


#TODO the parse_text_node_processor_action should probably be improved a bit. Maybe create APIs that are useful no matter if we are using text_node or table or whatever we may be doing

class A:

	class skip:
		@staticmethod
		def take_action(processor, node, match):
			pass

	class return_expression(public_base):
		expression = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return processor.context.eval_expression_dict(self.expression, dict(C=processor.context, P=processor, M=M, N=node, **M.named))

	class execute_snippet(public_base):
		snippet = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return processor.context.exec_expression_dict(self.snippet, dict(C=processor.context, P=processor, M=M, N=node, **M.named))

	class call_function(public_base):	#Deprecate?
		function = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return self.function(processor.context, processor, M, node, **M.named)


	class call_function_wpcam(public_base):	#with_processor_context_and_match
		function = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return self.function(C=processor.context, CX=processor.context.accessor, P=processor, M=M, N=node, **M.named)


	class call_function_with_match(public_base):
		function = RTS.positional()

		@RTS.initializer
		def deprecation_failure(self):
			raise Exception('deprecated')

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return self.function(M, node, **M.named)

	#Figure out which ones to keep and where to put them

	class call_function_with_accessor(public_base):
		function = RTS.positional()

		def take_action(self, processor, node, match):
			M = match_iterator(match)
			return self.function(processor.context, processor.context.accessor, processor, M, node, **M.named)

parse_text_node_processor_action = simple_priority_translator.from_raster(r'''

	pattern							expression
	-------							----------
	return {expression}				A.return_expression(M.pending_positional)

''', pattern_processor=regex_parser, post_processor=single_item, context=context.from_this_frame()).process_text



class improved_text_node_processor(public_base):
	rules = RTS.all_positional(field_type=RTS.SETTING)
	context = RTS.setting(factory=context.from_frame, factory_positionals=(sys._getframe(0),))
	pattern_processor = RTS.setting()
	action_processor = RTS.setting(parse_text_node_processor_action)
	post_processor = RTS.setting(tuple)
	default_action = RTS.setting(None)
	empty_action = RTS.setting(None)
	include_blanks = RTS.setting(False)

	@RTS.initializer
	def parse_actions(self):
		if isinstance(self.default_action, str):
			self.default_action = self.action_processor(self.default_action)

		if isinstance(self.empty_action, str):
			self.empty_action = self.action_processor(self.empty_action)


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
			rules.append((re_pattern, parsed_action))	#TODO - should be specific rule

		instance.rules += tuple(rules)

		return instance

	#def process_matched_expression(self, match, context, expression):
		#assert expression, f'Encountered empty expression when evaluating match {match} using {self.tokenizer}'
		#return context.eval_expression_dict(expression, dict(processor=self, node, **match.groupdict()))

	def process_node(self, node):
		if node.title is None:	#TODO - should this be an error when include_blanks is False? or configurable behavior?
			if self.empty_action:
				return self.empty_action.take_action(self, None, unconditional_match(''))
			else:
				raise Exception('Empty node was not handled')

		for pattern, action in self.rules:
			if match := pattern.match(node.title):
				return action.take_action(self, node, match)

		else:	#Apparently for elif is not a thing
			if self.default_action:
				return self.default_action.take_action(self, node, unconditional_match(node.title))
			else:
				raise Exception(node.title)

	def process_tree_iteratively(self, tree):
		for node in tree.iter_nodes(include_blanks=self.include_blanks):
			yield self.process_node(node)

	def process_tree(self, tree):
		return self.post_processor(self.process_tree_iteratively(tree))

	def process_text(self, text):
		return self.process_tree(text_node.from_text(text))

	def process_text_item(self, text):
		return self.process_node(text_node.from_text(text))

	def process_path(self, path):
		return self.process_tree(text_node.from_path(path))
