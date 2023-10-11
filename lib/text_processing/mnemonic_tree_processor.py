from .. import type_system as RTS
from ..type_system.bases import public_base
from ..rudimentary_features.code_manipulation.templating.pp_context import context
from ..type_system.features import classmethod_with_specified_settings, method_with_specified_settings
from ..table_processing.table import table
from .improved_tokenization import regex_parser
from .re_match_processing import match_iterator
from .improved_text_node_processor import improved_text_node_processor, A
from . import command_pattern_processor
from ..data_utils import attribute_stack, attribute_dict_ro_access
import re

#TODO - we need to rework the command processor a bit because now we get a regex and it has some captures but the post processing stage is missing



class check_cell_in_column(public_base):
	column = RTS.positional()
	condition = RTS.positional()

	def check_table_row(self, column_lut, row):
		index = column_lut.get(self.column, self.column)
		return self.condition(row[index])

def is_empty(value):
	return not bool(value.strip())


class mnemonic_tree_processor(improved_text_node_processor):
	#TODO - we should harmonize the various ways we interpret mnemonics into patterns and such so we don't duplicate so much
	rules = RTS.factory(list)
	name = RTS.setting(None)
	development_mode = RTS.setting(False)
	#post_processor = RTS.setting(lambda x: T.document(*x))

	#@method_with_specified_settings(RTS.ALL)	#NOT implemented yet, explicitly define
	@method_with_specified_settings(RTS.SELF)	#We skip table settings now until RTS.ALL is supported
	def empty_copy(self, config):
		result = self.__class__._from_config(config)
		result.rules = list()	#New list of rules
		result.default_action = None
		return result

	def optional_text_mnemonic(self, mnemonic):
		return pending_mnemonic_rules(self,
			self.pattern_processor(f'{mnemonic}[:]'),
			self.pattern_processor(f'{mnemonic}[:] {{text...}}'),
		)

	def mnemonic_rule(self, mnemonic):
		return pending_mnemonic_rules(self, self.pattern_processor(mnemonic))

	def add_mnemonic_action(self, mnemonic, action):
		self.rules.append((self.pattern_processor(mnemonic), action))


	@classmethod_with_specified_settings(RTS.SELF, table)
	def from_raster_table(cls, raster_table, *, config, table_config):
		raise Exception('deprecated')
		tbl = table.from_raster.call_with_config(table_config, raster_table)
		instance = cls._from_config(config, rules=[])
		match tbl.columns:
			case ['mnemonic', 'snippet']:
				for mnemonic, snippet in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):
					instance.add_mnemonic_action(mnemonic.strip(), A.execute_snippet(snippet))

			case ['mnemonic', 'function']:
				for mnemonic, function_snippet in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):
					mnemonic_pattern = command_pattern_processor.command_pattern_processor.process_text(mnemonic.strip())
					function = config.context.create_bound_function_from_snippet(function_snippet, 'C', 'CX', 'P', 'M', 'N', *(c.name for c in mnemonic_pattern.iter_captures()))	#TODO - check if we do 'N', 'M' somewhere else
					instance.rules.append((re.compile(rf'^{mnemonic_pattern.to_pattern()}$', re.I), A.call_function_with_accessor(function)))

			case ['mnemonic', 'expression']:
				for mnemonic, expression in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):
					instance.add_mnemonic_action(mnemonic.strip(), A.return_expression(expression))

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

		return instance


	def add_contextual_mnemonic_function(self, context, mnemonic, body):
		mnemonic_pattern = command_pattern_processor.command_pattern_processor.process_text(mnemonic.strip())	#TODO - configurable?
		#(C=processor.context, CX=processor.context.accessor, P=processor, M=M, N=node, **M.named)

		args = ', '.join(('C', 'CX', 'P', 'M', 'N', *(c.name for c in mnemonic_pattern.iter_captures())))

		if self.development_mode:
			if not body:
				body = 'print("DEV MODE MATCH")'
		else:
			assert body

		function = context.create_function2(body, args)
		rule = (re.compile(rf'^{mnemonic_pattern.to_pattern()}$', re.I), A.call_function_wpcam(function))
		self.rules.append(rule)
		return rule

	def add_contextual_regex_function(self, context, regex, body):

		#(C=processor.context, CX=processor.context.accessor, P=processor, M=M, N=node, **M.named)
		pattern = re.compile(rf'^{regex}$')
		args = ', '.join(('C', 'CX', 'P', 'M', 'N', *pattern.groupindex))
		function = context.create_function2(body, args)
		rule = (pattern, A.call_function_wpcam(function))
		self.rules.append(rule)
		return rule

	def add_contextual_default_function(self, context, body):

		args = ', '.join(('C', 'CX', 'P', 'M', 'N'))

		if self.development_mode:
			if not body:
				body = 'print("DEV MODE MATCH")'
		else:
			assert body

		function = context.create_function2(body, args)
		self.default_action = A.call_function_wpcam(function)
		return self.default_action



		# raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature

		# args = ', '.join(('M', 'N'))
		# function = context.create_function2(body, args)
		# self.default_action = A.call_function_wpcam(function)
		# return self.default_action

	def process_tree_extended(self, sub_processor, body, /, **stacked):
		#TBD - should we work on stacked dicts or stacked contexts?
		context = self.context
		with context.stack(**stacked):
			with attribute_stack(sub_processor, context=context):
				sub_processor.process_tree(body)

			return attribute_dict_ro_access(stacked)



	def process_tree_in_sub_context(self, sub_processor, body, /, **stacked):
		#TBD - should we work on stacked dicts or stacked contexts?
		sub_context = self.context.stacked_context(**stacked)
		with attribute_stack(sub_processor, context=sub_context):
			return sub_context, sub_processor.process_tree(body)



	def sub_process_tree(self, sub_processor, body, /, **stacked):
		#TBD - should we work on stacked dicts or stacked contexts?
		context = self.context
		with context.stack(**stacked):
			with attribute_stack(sub_processor, context=context):
				return sub_processor.process_tree(body)

	def sub_process_node(self, sub_processor, body, /, **stacked):
		#TBD - should we work on stacked dicts or stacked contexts?
		context = self.context
		with context.stack(**stacked):
			with attribute_stack(sub_processor, context=context):
				return sub_processor.process_node(body)

	@classmethod_with_specified_settings(RTS.SELF, table)
	def from_raster_table2(cls, raster_table, *, config, table_config):
		tbl = table.from_raster.call_with_config(table_config, raster_table)
		instance = cls._from_config(config, rules=[])



		match tbl.columns:
			# case ['mnemonic', 'snippet']:
			# 	for mnemonic, snippet in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):
			# 		instance.add_mnemonic_action(mnemonic.strip(), A.execute_snippet(snippet))

			case ['mnemonic', 'function']:

				sub_context = config.context.stacked_context(P=instance)
				sub_context.locals.update(C = config.context, CX = config.context.accessor)

				for mnemonic, function_snippet in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):

					instance.add_contextual_mnemonic_function(sub_context, mnemonic, function_snippet)

					#mnemonic_pattern = command_pattern_processor.command_pattern_processor.process_text(mnemonic.strip())

					#TODO - check if we do 'N', 'M' somewhere else
					#args = ', '.join(('M', 'N', *(c.name for c in mnemonic_pattern.iter_captures())))
					#function = sub_context.create_function2(function_snippet, args)
					#instance.rules.append((re.compile(rf'^{mnemonic_pattern.to_pattern()}$', re.I), A.call_function_with_match(function)))


			# case ['mnemonic', 'expression']:
			# 	for mnemonic, expression in tbl.strict_iter(multiline_condition=check_cell_in_column(0, is_empty), multiline_columns=(1,)):
			# 		instance.add_mnemonic_action(mnemonic.strip(), A.return_expression(expression))

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

		return instance





	@RTS.setting
	def pattern_processor(pattern):
		inner = command_pattern_processor.command_pattern_processor.process_text(pattern).to_pattern()
		return re.compile(rf'^{inner}$', re.I)


class pending_mnemonic_rules(public_base):
	processor = RTS.positional()
	mnemonic_rules = RTS.all_positional()


	def __call__(self, function):
		for mnemonic in self.mnemonic_rules:
			handler = self.processor.context.create_bound_function(function, 'M', 'N', *mnemonic.groupindex)
			self.processor.rules.append((mnemonic, call_mnemonic_handler(handler)))

		return function


class call_mnemonic_handler(public_base):
	#TODO - allow for context other than processors? Maybe that should be its own action to keep things clean
	handler = RTS.positional()

	def take_action(self, processor, node, match):
		M = match_iterator(match)
		return self.handler(M, node, **M.named)

