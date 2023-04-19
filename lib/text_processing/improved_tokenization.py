from .. import type_system as RTS
from ..type_system.bases import public_base
from ..type_system.features import classmethod_with_specified_settings, method_with_specified_settings
from ..rudimentary_features.code_manipulation.templating.pp_context import context
from ..table_processing.table import table
from ..text_processing.tokenization import call_processor_for_match, LEAVE_TOKENIZER, SKIP
from ..text_processing.re_tokenization import re_tokenize, UNMATCHED
from ..text_processing.re_match_processing import match_iterator
from ..exceptions import TokenizationUnhandledAction

import sys, re, types

class A:	#Actions - TODO - these should simply be a module
	from .tokenization import yield_value,  enter_tokenizer, yield_from_tokenizer

	class call_function(public_base):
		function = RTS.positional()

		def take_action_for_re_match(self, processor, text, start, config, match):
			#C, CX, P, M, T
			#if len(match.groups)
			if (g := match.groups()) == 0:
				[primary_token] = g
			else:
				primary_token = match.group()

			return self.function(processor.context, processor.context.accessor, processor, match, primary_token)


class improved_tokenizer(public_base):
	#NOTE - changing to positional in accordance with other rule systems (todo: harmonize)
	rules = RTS.positional(factory=list, field_type=RTS.SETTING)
	default_action = RTS.setting(None)
	last_match = RTS.state(None)

	#NOTE this should be upgraded to also use the conditional action system from priority_translator

	#Figure out where we stand on things that can be instanciated with all_positional but where we may want a fallback - specific fallback for zero args? lots of options, here is one
	@classmethod_with_specified_settings(RTS.SELF)
	def create_mutable(cls, config):
		config._target.update(rules = list())
		tokenizer = cls._from_config(config)
		return tokenizer

	def __repr__(self):
		return f'{self.__class__.__qualname__}({len(self.rules)} rules, default_action={self.default_action!r})'

	@method_with_specified_settings(RTS.SELF)
	def tokenize(self, text, start=0, level=0, *, config):
		token_gen = re_tokenize(text, config.rules, start)
		while True:
			try:
				action, match = next(token_gen)
			except StopIteration:
				return

			self.last_match = match

			if action is UNMATCHED and config.default_action:
				action = config.default_action

			if isinstance(action, A.enter_tokenizer):
				if action.post_filter:
					yield action.post_filter(action.tokenizer.process_text(text, self.last_match.end(), level+1))
				else:
					yield action.tokenizer.process_text(text, self.last_match.end(), level+1)
				token_gen = re_tokenize(text, config.rules, action.tokenizer.last_match.end())

			elif isinstance(action, A.yield_from_tokenizer):
				for item in action.tokenizer.process_text(text, self.last_match.end(), level+1):
					if action.post_filter:
						yield action.post_filter(item)
					else:
						yield item
				token_gen = re_tokenize(text, config.rules, action.tokenizer.last_match.end())

			elif action is SKIP:
				pass
			elif action is LEAVE_TOKENIZER:
				if level > 0:
					return
				else:
					raise Exception(f'Can not leave top level tokenizer {self}')

			elif action is UNMATCHED:
				raise TokenizationUnhandledAction(self, text, start, level, config, match)
				#raise Exception(f'No action for {match!r} in {self}')

			else:	#TODO - should check using ABC that this is a proper action

				#TODO - maybe it would be better to instead of matching things here have an API that would also s upport entering a sub tokenizer
				#		the API would have to have ways to affect the current state, maybe we could create a mutable state object and use in the API.

				match action.take_action_for_re_match(self, text, start, config, match):
					case A.yield_value(value=value):
						yield value
					case A.enter_tokenizer(tokenizer=sub_tokenizer, post_filter=post_filter):
						if post_filter:
							yield post_filter(sub_tokenizer.process_text(text, self.last_match.end(), level+1))
						else:
							yield sub_tokenizer.process_text(text, self.last_match.end(), level+1)
						token_gen = re_tokenize(text, config.rules, sub_tokenizer.last_match.end())
					case resulting_action if resulting_action is SKIP:
						pass

					case _ as action if action is LEAVE_TOKENIZER:	#Yes - this is horrible - we should rewrite this function because it is doing matching in two layers,
						#Maybe it should be a resolving loop?		(TODO)
						if level > 0:
							return
						else:
							raise Exception(f'Can not leave top level tokenizer {self}')

					case _ as unhandled:
						raise Exception(f'The value {unhandled!r} could not be handled')


				#yield action.take_action_for_re_match(self, text, start, config, match)






class simple_priority_translator(public_base):
	tokenizer = RTS.positional(factory=improved_tokenizer)
	context = RTS.setting(factory=context.from_frame, factory_positionals=(sys._getframe(0),))
	default_expression = RTS.setting(None)
	pattern_processor = RTS.setting(re.compile)
	post_processor = RTS.setting(tuple)

	def process_matched_expression(self, match, context, expression):
		assert expression, f'Encountered empty expression when evaluating match {match} using {self.tokenizer}'
		return context.eval_expression_dict(expression, dict(M=match_iterator(match), self=self, _=match.group(0)))

	@classmethod_with_specified_settings(RTS.SELF)
	def from_raster(cls, raster_table, config):
		context = config.context
		pattern_processor = config.pattern_processor
		rules = list()
		instance = cls(**config._target)
		PME = types.MethodType(cls.process_matched_expression, instance)

		for pattern, expression in table.from_raster(raster_table).strict_iter('pattern', 'expression'):
			rules.append((pattern_processor(pattern), call_processor_for_match(PME, context, expression)))

		instance.tokenizer.rules += tuple(rules)
		if config.default_expression:	#Only configure default_action if default_expression is configured, this makes errors easier to follow
			instance.tokenizer.default_action = call_processor_for_match(PME, context, config.default_expression)

		return instance

	@classmethod_with_specified_settings(RTS.SELF)
	def process_text(self, pattern, *, config):
		if post_processor := config.post_processor:
			return post_processor(self.tokenizer.tokenize(pattern))
		else:
			return self.tokenizer.tokenize(pattern)



class simple_regex_parser(simple_priority_translator):
	re_flags = RTS.setting(0)
	post_processor = RTS.setting(None)

	def process_text(self, pattern):
		return re.compile(''.join(super().process_text(pattern)), self.re_flags)




regex_parser = simple_regex_parser.from_raster(r'''

	pattern			expression
	-------			----------
	\{\{			r'{'
	\}\}			r'}'
	\{(\S+)\}		f'(?P<{M.pending_positional}>.*)'
	\s+				r'\s+'

''', default_expression='re.escape(M.text)', re_flags=re.I).process_text

class bootstrap_processor(public_base):
	translator = RTS.positional(factory=simple_priority_translator)
	context = RTS.setting(factory=context.from_frame, factory_positionals=(sys._getframe(0),))
	pattern_processor = RTS.setting(regex_parser)

	#TODO - _context and _processor shoudl be harmonized to C and P, or .. perhaps it should be configurable somewhere?
	def process_matched_expression(self, match, context, expression):
		assert expression, f'Encountered empty expression when evaluating match {match} using {self.tokenizer}'
		return context.eval_expression_dict(expression, dict(_processor=self, _context=context, **match.groupdict()))

	@classmethod_with_specified_settings(table, RTS.SELF)
	def from_raster(cls, raster_table, *, table_settings, processor_settings):
		table_reference = table.from_raster.call_with_config(table_settings, raster_table)
		return cls.from_table.call_with_config(table_settings, processor_settings, table_reference)

	@classmethod_with_specified_settings(table, RTS.SELF)
	def from_table(cls, table_reference, *, table_settings, processor_settings):
		translator = simple_priority_translator()
		instance = cls(translator)

		PME = types.MethodType(cls.process_matched_expression, instance)
		rules = list()

		for pattern, expression in table_reference.strict_iter('pattern', 'expression'):

			regex = processor_settings.pattern_processor(pattern)

			action = call_processor_for_match(PME, processor_settings.context, expression)
			rules.append((regex, action))

		translator.tokenizer.rules += tuple(rules)

		return instance




	def process_text(self, text):
		[result] = self.translator.process_text(text)
		return result


class sub_tokenizer(public_base):
	context = RTS.positional()
	tokenizer = RTS.positional()
	expression = RTS.positional(default=None)

	def take_action_for_re_match(self, tokenizer, text, start, config, match):
		sub_tokenizer = self.context.eval_expression_dict(self.tokenizer, dict(_context=self.context, M=match_iterator(match), _=match.group(0)))
		return A.enter_tokenizer(sub_tokenizer)

	# def process_sub_tokens(self, tokenizer, sub_tokens):
	# 	if self.expression:
	# 		return self.context.eval_expression_dict(self.expression, dict(_context=self.context, _=sub_tokens))
	# 	#elif tokenizer_post_processor := getattr(tokenizer, 'post_processor'):
	# 	#	return tokenizer_post_processor(sub_tokens)
	# 	else:
	# 		return sub_tokens





class return_expression(public_base):
	context = RTS.positional()
	expression = RTS.positional()

	def __repr__(self):
		return f'{self.__class__.__name__}({self.expression!r})'

	def take_action_for_re_match(self, tokenizer, text, start, config, match):
		return A.yield_value(self.context.eval_expression_dict(self.expression, dict(_context=self.context, M=match_iterator(match), _=match.group(0))))



class extended_tokenizer(improved_tokenizer):
	default_action = RTS.setting(None)
	post_processor = RTS.setting(tuple)
	context = RTS.setting(factory=context.from_frame, factory_positionals=(sys._getframe(0),))

	def add_contextual_default_function(self, context, body):
		args = 'C, CX, P, M, T'
		function = context.create_function2(body, args)
		self.default_action = A.call_function(function)
		return self.default_action	#TODO - possibly wrap this to indicate it is a default action? (This is just for metadata/introspection)

	def add_contextual_regex_function(self, context, pattern, body):
		args = 'C, CX, P, M, T'
		function = context.create_function2(body, args)
		rule = (pattern, A.call_function(function))
		self.rules.append(rule)
		return rule

	def extend(self, other):
		self.rules += other.rules
		if not self.default_action:
			self.default_action = other.default_action

	@method_with_specified_settings(RTS.SELF)
	def process_text(self, text, start=0, level=0, *, config):
		return config.post_processor(self.tokenize.call_with_config(config, text, start, level))

	@classmethod_with_specified_settings(table, RTS.SELF)
	def from_raster(cls, action_processor, raster_table, *, table_settings, processor_settings):
		return cls.from_table.call_with_config(table_settings, processor_settings, action_processor, table.from_raster.call_with_config(table_settings, raster_table))

	__call__ = process_text


	@classmethod_with_specified_settings(table, RTS.SELF)
	def from_table(cls, action_processor, table_reference, *, table_settings, processor_settings):

		processor_settings._conditional_process_settings(
			processors = dict(
				default_action = action_processor
			),
			conditions = dict(
				default_action = lambda x: bool(x) and bool(x.strip())
			),
		)

		instance = cls._from_config(processor_settings)

		#PME = types.MethodType(cls.process_matched_expression, instance)
		rules = list()

		for pattern_type, pattern, action in table_reference.strict_iter.call_with_config(table_settings, 'type', 'pattern', 'action'):
			#print(pattern, action_processor(action))

			#TODO - actually eval these types in context
			if pattern_type == 'literal':
				rules.append((re.compile(re.escape(pattern)), action_processor(action)))
			elif pattern_type == 'regex':
				rules.append((re.compile(pattern), action_processor(action)))
			else:
				raise Exception(pattern_type)

		instance.rules += tuple(rules)



		# if default_action:	#Only configure default_action if default_expression is configured, this makes errors easier to follow

		# 	#TODO - figure this out!
		# 	match action_processor(default_action):
		# 		# case include_tokenizer() as inclusion:
		# 		# 	print(inclusion.context.eval_expression_dict(inclusion.tokenizer, dict(_context=inclusion.context)))


		# 		case _ as default_action:
		# 			instance.default_action = default_action



		return instance



bootstrap_action_processor_table = table.from_raster(r'''

	pattern									expression
	-------									----------
	enter {tokenizer} as {expression}		sub_tokenizer(_context, tokenizer, expression)
	leave									LEAVE_TOKENIZER
	return {expression}						return_expression(_context, expression)
	skip									SKIP

	enter {tokenizer}						sub_tokenizer(_context, tokenizer)


''')


bootstrap_action_processor_context = context.selectively_create_from_this_frame(
	*'sub_tokenizer LEAVE_TOKENIZER return_expression SKIP bootstrap_processor'.split()
)


