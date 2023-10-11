from .. import type_system as RTS
from ..type_system.bases import public_base

from ..type_system.features import method_with_specified_settings
from ..improved_mnemonic_tree_processor.tree_node_processing import rule, call_bound_function_with_configuration_item_and_regex_match
from ..improved_mnemonic_tree_processor.context import context

from ..improved_mnemonic_tree_processor import conditions as C
from ..improved_mnemonic_tree_processor import actions as A


from ..iteration_utils import take_while_consequtive
from ..string_utils import to_identifier
from ..text_nodes import text_node
from ..text_processing import command_pattern_types as CPT
from ..type_system.features import method_with_specified_settings



class improved_text_processor(public_base):
	rules = RTS.optional_factory(list)
	context = RTS.setting(factory=context.from_this_frame, factory_positionals=(3,), factory_named=dict(name='default_context'))	#Why 3? Will it change? Is this a terrible practice?
	default_action = RTS.setting(None)
	name = RTS.setting(None)		#Should possibly not be config though
	workdir = RTS.setting(None)

	def add_rule(self, condition, action):
		self.rules.append(rule(condition, action))


	#Maybe the action processor should be a whole own module - then we could also have one built in and one that can be extended
	#TODO - this is copied from improved_mnemonic_tree_processor - go over and make sure it is relevant
	@method_with_specified_settings(RTS.SELF)
	def process_action(self, action, match, *, config):
		match action:
			case A.return_value(value):
				return value

			case A.return_processed_match(processor):
				return processor(match)

			case A.execute_node_body_in_context(context):
				get_context(context).exec(get_node_body(match).text)
				return OK

			case A.call_function_using_regex_match_as_arguments(function):
				positional, named = get_match_as_arguments(match)

				positional = process_positionals(action.positional_processors, positional)
				named = process_named(action.named_processors, named)

				positional += resolve_positionals(action.additional_positional)
				named.update(resolve_named(action.additional_named))

				return function(*positional, **named)

			case A.call_function_with_regex_match(function):
				positional = (get_match_as_arguments(match),)
				positional += resolve_positionals(action.additional_positional)

				return function(*positional, **action.additional_named)

			case A.call_function_with_node_and_regex_args(function):
				positional, named = get_match_as_arguments(match)
				positional = (config.context, match.item, *positional, *resolve_positionals(action.additional_positional))
				named.update(resolve_named(action.additional_named))

				return function(*positional, **named)


			case A.bind_and_call_function_with_processor_config_and_regex_args(function):
				return call_bound_function_with_configuration_item_and_regex_match(function.__get__(self, self.__class__), (config,), match)

			case _ if action is A.return_match:
				return match

			case _ if action in A.TRANSPARENT_ACTION_SET:
				return action

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	#TODO - this is copied from improved_mnemonic_tree_processor - go over and make sure it is relevant
	@method_with_specified_settings(RTS.SELF)
	def process_text(self, text, *, config):
		for rule in self.rules:
			if match := rule.check_match(text):
				return self.process_action.call_with_config(config, rule.action, match)

		if self.default_action:
			return self.process_action.call_with_config(config, self.default_action, M.matched_unconditionally(text))

		raise Exception(f'The text {text!r} could not be handled by {self}')

	def __repr__(self):	#This is a common repr, we should reuse it
		if self.name:
			return f'{self.__class__.__qualname__}({self.name!r})'
		else:
			return f'{self.__class__.__qualname__}({hex(id(self))})'





def create_text_processor_handler(config, node, capture_names, function_name):
	#Acquire references to current context and an accessor for it
	ctx = config.context

	#Make sure parameters are not overlapping with capture names and prepare parameters
	parameters = 'processor', 'config', 'node'
	assert not (set(capture_names) & set(parameters))
	if capture_names:
		parameters += ('*', *capture_names)

	#Create text representation of arguments and prepare the python code for the handler function
	arguments = ', '.join(parameters)
	python_code = text_node.from_title_and_body(f'def {function_name}({arguments}):', node.body.dedented_copy()).text

	#Create a sub context for defining the handler to avoid name clashing or namespace pollution
	sc = ctx.sub_context()
	sc.exec(python_code)
	#Process the new function using the @method_with_specified_settings(RTS.SELF) decorator
	new_function = method_with_specified_settings(RTS.SELF)(sc.require(function_name))

	return new_function

def create_text_processor_rule(processor, config, node, condition, capture_names, function_name):
	cx = config.context.accessor
	new_function = create_text_processor_handler(config, node, capture_names, function_name)
	#Add the new rule for the target tree processor
	cx.target_processor.add_rule(condition, A.bind_and_call_function_with_processor_config_and_regex_args(new_function))

@method_with_specified_settings(RTS.SELF)
def create_text_processor_rule_for_mnemonic(processor, config, node, *, mnemonic):
	#Create mnemonic matching condition and get the capture names
	condition = C.matches_mnemonic(mnemonic)
	capture_names = tuple(c.name for c in condition.mnemonic_captures)

	#Figure out function name based on text literals in the mnemonic pattern
	function_name = to_identifier(i.text for i in take_while_consequtive(CPT.is_literal, condition.mnemonic_pattern.sequence))
	create_text_processor_rule(processor, config, node, condition, capture_names, function_name)

@method_with_specified_settings(RTS.SELF)
def create_text_processor_rule_for_regex(processor, config, node, *, pattern):
	#Create regex matching condition and get the capture names
	condition = C.matches_regex(f'^{pattern}$')
	capture_names = tuple(c.name for c in condition.regex_captures)
	create_text_processor_rule(processor, config, node, condition, capture_names, 'regex_handler')

@method_with_specified_settings(RTS.SELF)
def create_text_processor_rule_for_literal(processor, config, node, *, pattern):
	#Create literal matching condition
	condition = C.matches_literal(pattern)
	create_text_processor_rule(processor, config, node, condition, (), 'literal_handler')

@method_with_specified_settings(RTS.SELF)
def set_text_processor_default_rule(processor, config, node):
	cx = config.context.accessor
	new_function = create_text_processor_handler(config, node, (), 'default')
	#Add the new rule for the target tree processor
	assert not processor.default_action
	cx.target_processor.default_action = A.bind_and_call_function_with_processor_config_and_regex_args(new_function)

