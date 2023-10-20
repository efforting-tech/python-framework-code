import re

from .. import type_system as RTS
from ..type_system.bases import public_base

#TODO - improved_mnemonic_tree_processor.context shoudl be moved out to generic processing
from ..improved_mnemonic_tree_processor.context import context, reference
from ..improved_mnemonic_tree_processor import actions as A

from ..type_system.features import method_with_specified_settings
from ..text_processing.re_tokenization import unconditional_match, hacky_pattern_str, hacky_pattern_bytes


class continue_at_position(public_base):
	position = RTS.positional()

#TODO - we should have a common rule system and maybe a common processor-API to harmonize things
class rule(public_base):
	condition = RTS.positional()
	action = RTS.positional(default=None)

	def check_match(self, item):
		return self.condition.check_match(item)

class tokenization_result(public_base):
	tokenizer = RTS.positional()
	text = RTS.positional()
	start = RTS.positional(default=0)
	tokens = RTS.factory(list)

	first_pos = RTS.state(None)
	last_pos = RTS.state(None)
	tail_pos = RTS.state(None)

	@property
	def has_contents(self):
		return (
			(self.first_pos is not None)
			or (self.last_pos is not None)
			or (self.tail_pos is not None)
			or bool(self.tokens)
		)

	def join(self, separator=''):
		def get_value(v):
			match v:
				case str():
					return v
				case re.Match():
					return v.group()
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		return separator.join(map(get_value, self.tokens))

	#Do we need both flavors of append? TODO: Motivate or clean up
	def append(self, match, value):
		self.tokens.append(value)
		if self.first_pos is None:
			self.first_pos = match.start()

		self.last_pos = match.end()

		if isinstance(value, tokenization_result):
			self.tail_pos = value.tail_pos

	def append_sub_result(self, sub_result):
		if sub_result.has_contents:
			self.tokens.append(sub_result)
			if self.first_pos is None:
				self.first_pos = sub_result.first_pos

			self.last_pos = sub_result.last_pos
			self.tail_pos = sub_result.tail_pos


class improved_tokenizer(public_base):
	rules = RTS.optional_factory(list)
	context = RTS.setting(factory=context.from_this_frame, factory_positionals=(3,), factory_named=dict(name='default_context'))	#Why 3? Will it change? Is this a terrible practice?
	default_action = RTS.setting(None)
	name = RTS.setting(None)		#Should possibly not be config though
	must_leave = RTS.setting(False)
	hacky_pattern = RTS.setting(hacky_pattern_str)

	def add_rule(self, condition, action):
		self.rules.append(rule(condition, action))

	def potential_match(self, text, start=0, end=None):
		if text[start:end]:
			return self.hacky_pattern.match(text[:end], start)


	@method_with_specified_settings(RTS.SELF)
	def exhaust_text(self, text, start=0, *, config):
		pos = start
		result = tokenization_result(self, text, pos)
		while True:
			sub_result = self.process_text.call_with_config(config, text, pos)
			result.append_sub_result(sub_result)

			if sub_result.tail_pos is not None and sub_result.tail_pos < len(text):
				pos = sub_result.tail_pos + 1
			else:
				return result

	@method_with_specified_settings(RTS.SELF)
	def process_text(self, text, start=0, *, config):
		result = tokenization_result(self, text, start)
		pending_action = None

		def process_sub_result(match, sub_result):
			nonlocal pending_action
			match sub_result:
				case A.enter_sub_tokenizer_after():
					pending_action = sub_result

				case A.leave_tokenizer_after:
					result.tail_pos = match.end()
					pending_action = A.break_loop

				case A.leave_tokenizer_before:
					result.tail_pos = match.start()
					pending_action = A.break_loop

				case A.skip:
					pass	#Just swallow

				case tuple():
					for sub_sub_result in sub_result:
						process_sub_result(match, sub_sub_result)

				case _:
					result.append(match, sub_result)


		def take_action(action, match):
			nonlocal pending_action
			#TODO - cover more cases (can we detect poor coverage too?)
			match action:
				case A.skip:
					pass

				case A.return_match:	#TODO maybe we want emit_match or append_match instead
					result.append(match, match)

				case A.return_processed_match(processor):
					result.append(match, processor(match))

				case A.return_value(value):
					result.append(match, value)

				case A.return_result_before:
					result.tail_pos = match.start()
					pending_action = A.break_loop

				case A.return_result_after:
					result.tail_pos = match.end()
					pending_action = A.break_loop

				case A.call_function_using_regex_match_as_arguments():
					from ..text_processing.tokenization import extract_positionals_and_keyword_arguments_from_match
					from ..improved_mnemonic_tree_processor.tree_node_processing import process_positionals, process_named, resolve_positionals, resolve_named

					positional, named = extract_positionals_and_keyword_arguments_from_match(match)

					positional = process_positionals(action.positional_processors, positional)
					named = process_named(action.named_processors, named)

					positional += resolve_positionals(action.additional_positional)
					named.update(resolve_named(action.additional_named))

					sub_result = action.function(self, config, match, **named)
					process_sub_result(match, sub_result)


				case A.call_function_with_regex_match():
					from ..text_processing.tokenization import extract_positionals_and_keyword_arguments_from_match
					from ..improved_mnemonic_tree_processor.tree_node_processing import process_positionals, process_named, resolve_positionals, resolve_named
					sub_result = action.function(self, config, match)
					process_sub_result(match, sub_result)


				case A.call_function_with_regex_match_and_text():
					from ..text_processing.tokenization import extract_positionals_and_keyword_arguments_from_match
					from ..improved_mnemonic_tree_processor.tree_node_processing import process_positionals, process_named, resolve_positionals, resolve_named
					sub_result = action.function(self, config, match, match.group())
					process_sub_result(match, sub_result)

				case tuple():
					for sub_action in action:
						take_action(sub_action, match)

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')

		pos = start

		while pos <= len(text):
			closest_rule, closest_match = None, None
			for rule in self.rules:
				if match := rule.condition.search(text, pos):
					if (closest_rule is None) or (match.start() < closest_match.start()):
						closest_rule, closest_match = rule, match

						if match.start() == pos:
							break	#Early return


			if closest_match:
				#prepare advancing
				if pos == closest_match.end():
					pending_position = pos + 1
					pending_action = continue_at_position(pending_position)
				else:
					pending_position = closest_match.end()
					pending_action = continue_at_position(pending_position)

				#check for head
				if head := self.potential_match(text, pos, closest_match.start()):
					if not self.default_action:
						raise Exception(head)

					take_action(self.default_action, head)

				#deal with match
				take_action(closest_rule.action, closest_match)

			else:
				#check for tail
				if tail := self.potential_match(text, pos):
					if not self.default_action:
						raise Exception(tail)

					take_action(self.default_action, tail)

				break

			match pending_action:
				case continue_at_position(pending_pos):
					pos = result.tail_pos = pending_pos

				case A.enter_sub_tokenizer_after():
					assert not pending_action.pre_action
					#assert not pending_action.post_action
					sub_result = pending_action.tokenizer.process_text.call_with_config(config, text, pending_position, must_leave=True)

					if sub_result.tail_pos is None or (sub_result.last_pos is not None and sub_result.last_pos > sub_result.tail_pos):
						raise Exception(f'Reached end before proper exit of {pending_action.tokenizer}')

					if pending_action.post_action:
						result.append(closest_match, pending_action.post_action(sub_result))
					else:
						result.append(closest_match, sub_result)

					pos = result.pos = sub_result.tail_pos

				case A.break_loop:
					return result

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')

		if config.must_leave:
			raise Exception(f'Reached end before proper exit of {self}')

		return result