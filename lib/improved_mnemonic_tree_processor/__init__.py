from .. import type_system as RTS
from ..iteration_utils import take_while_consequtive
from ..string_utils import to_identifier
from ..text_nodes import text_node
from ..text_processing import command_pattern_types as CPT
from ..type_system.features import method_with_specified_settings
from . import conditions as C
from . import actions as A

#TODO - we should preprocess code also so we can use rich features, such as metadata or templating

def create_tree_processor_handler(config, node, capture_names, function_name):
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

def create_tree_processor_rule(processor, config, node, condition, capture_names, function_name):
	cx = config.context.accessor
	new_function = create_tree_processor_handler(config, node, capture_names, function_name)
	#Add the new rule for the target tree processor
	cx.target_processor.add_rule(C.title_condition(condition), A.bind_and_call_function_with_processor_config_and_regex_args(new_function))

@method_with_specified_settings(RTS.SELF)
def create_tree_processor_rule_for_mnemonic(processor, config, node, *, mnemonic):
	#Create mnemonic matching condition and get the capture names
	condition = C.matches_mnemonic(mnemonic)
	capture_names = tuple(c.name for c in condition.mnemonic_captures)

	#Figure out function name based on text literals in the mnemonic pattern
	function_name = to_identifier(i.text for i in take_while_consequtive(CPT.is_literal, condition.mnemonic_pattern.sequence))
	create_tree_processor_rule(processor, config, node, condition, capture_names, function_name)

@method_with_specified_settings(RTS.SELF)
def create_tree_processor_rule_for_regex(processor, config, node, *, pattern):
	#Create regex matching condition and get the capture names
	condition = C.matches_regex(f'^{pattern}$')
	capture_names = tuple(c.name for c in condition.regex_captures)
	create_tree_processor_rule(processor, config, node, condition, capture_names, 'regex_handler')

@method_with_specified_settings(RTS.SELF)
def create_tree_processor_rule_for_literal(processor, config, node, *, pattern):
	#Create literal matching condition
	condition = C.matches_literal(pattern)
	create_tree_processor_rule(processor, config, node, condition, (), 'literal_handler')

@method_with_specified_settings(RTS.SELF)
def set_tree_processor_default_rule(processor, config, node):
	cx = config.context.accessor
	new_function = create_tree_processor_handler(config, node, (), 'default')
	#Add the new rule for the target tree processor
	assert not processor.default_action
	cx.target_processor.default_action = A.bind_and_call_function_with_processor_config_and_regex_args(new_function)
