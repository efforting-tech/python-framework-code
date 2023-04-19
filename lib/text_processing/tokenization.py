from .. import type_system as RTS
from ..type_system.bases import public_base	#we should check where standard_base needs to be turned into public_base
from .. import abstract_base_classes as ABC
from ..symbols import register_symbol
from .re_tokenization import re_tokenize, SKIP, UNMATCHED

#IMPORTANT TODO - we should harmonize the re_tokenization and tokenization stuff to be compatible with PM


#TBD Do we want to use capitalized names to differentiate between a symbol or an instantiable type? Leaning towards not
#		a problem though is that a symbol node is callable. Another solution is to make the "singletons" be callables that returns the symbol.
#		let's try that for now

#However - a problem with this approach is that the symbol will not share a subclass. Maybe we should compose these.



LEAVE_TOKENIZER = register_symbol('internal.text.tokenizer.action.leave_tokenizer')

def leave_tokenizer():
	return LEAVE_TOKENIZER

def skip():
	return SKIP





def extract_positionals_and_keyword_arguments_from_match(match):
	pos = dict(enumerate(match.groups(), 1))
	kw = match.groupdict()
	kw_indices = set(match.re.groupindex.values())
	refined_pos = tuple(v for k, v in pos.items() if k not in kw_indices)
	return refined_pos, kw


#    _      _   _
#   /_\  __| |_(_)___ _ _  ___
#  / _ \/ _|  _| / _ \ ' \(_-<
# /_/ \_\__|\__|_\___/_||_/__/


#NOTE - we probably need an action that calls a function with the match for further processing

@ABC.register_class_tree('text.tokenizer.action')
class action(public_base):
	pass


class call_processor_for_match(action):
	#NOTE - classification is deprecated
	#classification = RTS.positional()	#TODO - should we have the classification stuff even? In some cases we don't use it, so maybe it should be only associated with certain structures
	processor = RTS.positional()
	additional_positionals = RTS.all_positional()
	named = RTS.all_named()

	def take_action_for_re_match(self, tokenizer, text, start, config, match):	#TODO - define API for this
		return yield_value(self.processor(match, *self.additional_positionals, **self.named))

class action_result(public_base):
	pass

class yield_value(action_result):
	#classification = RTS.positional()	#DEPRECATED
	value = RTS.positional()




# class yield_match(action):
# 	classification = RTS.positional()

# 	#NOTE: We may have symbols outside of C and this would fail then
# 	#	But we could later on have a "nice" repr that does contextual symbol look up similar to this deprecated method:
# 	#	CODE: __repr__ = field_based_representation('{self.classification._path.relative_to(C._path)}')

# 	#TODO: __repr__ = field_based_representation('{self.classification}')

# class yield_match_and_value(action):
# 	classification = RTS.positional()
# 	value = RTS.positional()


# class yield_matched_text(action):
# 	classification = RTS.positional()


# 	#TODO: __repr__ = field_based_representation('{self.classification}')

# class yield_classification(action):
# 	classification = RTS.positional()



class enter_tokenizer(action):
	tokenizer = RTS.positional()
	post_filter = RTS.positional(default=None)

class yield_from_tokenizer(action):
	tokenizer = RTS.positional()
	post_filter = RTS.positional(default=None)

# 	classification = RTS.positional()


# 	#TODO: __repr__ = field_based_representation('{self.tokenizer} → {self.classification}')




# @ABC.register_class_tree('text.tokenizer.match')
# class match(standard_base):
# 	pass

# class token_match(match):
# 	classification = RTS.positional()
# 	match = RTS.positional()


# 	#TODO: __repr__ = field_based_representation('{self.classification}, {self.match!r}')

# class token_value_match(token_match):
# 	value = RTS.positional()



class tokenizer(public_base):
	rules = RTS.positional(factory=list)
	#Changing to list - we should make a generic rule-system for all the different implementations we have (trees, processors, tokenizing etc)
	label = RTS.named(default=None)
	default_action = RTS.named(default=None)

	#TODO: __repr__ = field_based_representation('{self.label!r}')


	# @RTS.initializer
	# def _check_constructor_mutation_for_label(self):
	# 	#NOTE - this is a good example for how we shall handle mutation warnings in the project
	# 	match self.rules:
	# 		case [str(), _]:
	# 			raise Exception('First rule is a string, this is because now label is no longer a positional argument.')

	#TBD - should these be generators or perform the full tokenization up front? It depends on if we will allow manipulation of the result
	#		leaning towards making generators of these - which we may have to make not of wherever we use these
	# def inner_tokenize(self, text, start=0):
	# 	token_gen = re_tokenize(text, self.rules, start)
	# 	result = list()
	# 	while True:
	# 		action, match = next(token_gen)
	# 		#TODO - match statement? - harmonize stuff with below?
	# 		if action is UNMATCHED and self.default_action:
	# 			action = self.default_action

	# 		if isinstance(action, yield_match):
	# 			result.append(token_match(action.classification, match))
	# 		elif isinstance(action, yield_classification):
	# 			result.append(token_match(action.classification, None))
	# 		elif isinstance(action, yield_value):
	# 			result.append(token_match(action.classification, action.value))
	# 		elif isinstance(action, yield_match_and_value):
	# 			result.append(token_value_match(action.classification, match, action.value))
	# 		elif isinstance(action, yield_matched_text):
	# 			assert 0 <= match.re.groups <= 1
	# 			result.append(token_match(action.classification, match.group(match.re.groups)))
	# 		elif isinstance(action, call_processor_for_match):
	# 			result.append(token_value_match(action.classification, match, action.processor(match, *action.additional_positionals, **action.named)))
	# 		elif isinstance(action, enter_tokenizer):
	# 			sub_result, last_sub_match = action.tokenizer.tokenize(text, match.end())
	# 			token_gen = re_tokenize(text, self.rules, last_sub_match.end()+1)
	# 			result.append(sub_result)

	# 		elif action is LEAVE_TOKENIZER:
	# 			return tuple(result), match
	# 		else:
	# 			raise Exception(action)


	def tokenize(self, text, start=0):
		token_gen = re_tokenize(text, self.rules, start)
		result = list()
		while True:
			try:
				action, match = next(token_gen)
			except StopIteration:
				return tuple(result)

			if action is UNMATCHED and self.default_action:
				action = self.default_action

			# if isinstance(action, yield_match):
			# 	result.append(token_match(action.classification, match))
			# elif isinstance(action, yield_classification):
			# 	result.append(token_match(action.classification, None))
			# elif isinstance(action, yield_value):
			# 	result.append(token_match(action.classification, action.value))
			# elif isinstance(action, yield_match_and_value):
			# 	result.append(token_value_match(action.classification, match, action.value))
			# elif isinstance(action, yield_matched_text):
			# 	assert 0 <= match.re.groups <= 1
			# 	result.append(token_match(action.classification, match.group(match.re.groups)))
			# elif isinstance(action, call_processor_for_match):
			# 	result.append(token_value_match(action.classification, match, action.processor(match, *action.additional_positionals, **action.named)))
			if isinstance(action, call_processor_for_match):
				print(action)
			elif isinstance(action, enter_tokenizer):
				sub_result, last_sub_match = action.tokenizer.inner_tokenize(text, match.end())
				token_gen = re_tokenize(text, self.rules, last_sub_match.end())
				result.append(token_match(action.classification, sub_result))
			elif action is LEAVE_TOKENIZER:
				raise Exception('top level')
			else:
				raise Exception(action)

