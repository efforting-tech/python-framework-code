import re

from .. import type_system as RTS
from ..type_system.bases import public_base

#TODO - improved_mnemonic_tree_processor.context shoudl be moved out to generic processing
from ..improved_mnemonic_tree_processor.context import context, reference
from ..improved_mnemonic_tree_processor import actions as A
from ..data_utils.priority_translator import priority_translator

from ..type_system.features import method_with_specified_settings
from ..text_processing.re_tokenization import unconditional_match, hacky_pattern

def potential_match(text, start=0, end=None):
	if text[start:end]:
		return hacky_pattern.match(text[:end], start)

class tokenizer_state(public_base):
	result = RTS.positional()
	position = RTS.positional()
	pending_position = RTS.state(None)

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

	def append(self, match, value):
		self.tokens.append(value)
		if self.first_pos is None:
			self.first_pos = match.start()

		self.last_pos = match.end()

default_further_improved_tokenizer_action_resolver = priority_translator()		# priority_processor()

class further_improved_tokenizer(public_base):
	rules = RTS.optional_factory(list)
	context = RTS.setting(factory=context.from_this_frame, factory_positionals=(3,), factory_named=dict(name='default_context'))	#Why 3? Will it change? Is this a terrible practice?
	default_action = RTS.setting(None)
	name = RTS.setting(None)		#Should possibly not be config though
	action_resolver = RTS.setting(default=default_further_improved_tokenizer_action_resolver)

	def add_rule(self, condition, action):
		self.rules.append(rule(condition, action))

	def take_action(self, state, action, match):
		self.action_resolver.process_item(action, context=self.context.sub_context(state=state, match=match))

		# match action:
		# 	case continue_at_position(state.pending_position):
		# 		state.position = state.result.tail_pos = state.pending_position

		# 	# case A.enter_sub_tokenizer_after():
		# 	# 	assert not state.pending_action.pre_action
		# 	# 	#assert not state.pending_action.post_action
		# 	# 	sub_result = state.pending_action.tokenizer.process_text.call_with_config(config, text, state.pending_position)


		# 	# 	if sub_result.tail_pos is None or (sub_result.last_pos is not None and sub_result.last_pos > sub_result.tail_pos):
		# 	# 		raise Exception(f'Reached end before proper exit of {state.pending_action.tokenizer}')

		# 	# 	if state.pending_action.post_action:
		# 	# 		result.append(closest_match, state.pending_action.post_action(sub_result))
		# 	# 	else:
		# 	# 		result.append(closest_match, sub_result)
		# 	# 	state.position = result.state.position = sub_result.tail_pos



		# 	# case A.break_loop:
		# 	# 	break

		# 	case _ as unhandled:
		# 		raise Exception(f'The value {unhandled!r} could not be handled')




	@method_with_specified_settings(RTS.SELF)
	def process_text(self, text, start=0, *, config):
		result = tokenization_result(self, text, start)
		state = tokenizer_state(result, start)

		while state.position <= len(text):
			closest_rule, closest_match = None, None
			for rule in self.rules:
				if match := rule.condition.search(text, state.position):
					if (closest_rule is None) or (match.start() < closest_match.start()):
						closest_rule, closest_match = rule, match

						if match.start() == state.position:
							break	#Early return


			if closest_match:
				#prepare advancing
				if state.position == closest_match.end():
					state.pending_position = state.position + 1
					state.pending_action = continue_at_position(state.pending_position)
				else:
					state.pending_position = closest_match.end()
					state.pending_action = continue_at_position(state.pending_position)

				#check for head
				if head := potential_match(text, state.position, closest_match.start()):
					if not self.default_action:
						raise Exception(head)

					self.take_action(state, self.default_action, head)

				#deal with match
				self.take_action(state, closest_rule.action, closest_match)


			else:
				#check for tail
				if tail := potential_match(text, state.position):
					if not self.default_action:
						raise Exception(tail)

					self.take_action(state, self.default_action, tail)

				break


		return result