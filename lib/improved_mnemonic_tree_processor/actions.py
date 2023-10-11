from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol

return_match = register_symbol('internal.action.return_match')
no_action = register_symbol('internal.action.no_action')
skip = register_symbol('internal.action.skip')
insert_blank_node = register_symbol('internal.action.skip')

add_and_return_result = register_symbol('internal.add_and_return_result')
return_result_before = register_symbol('internal.return_result_before')
return_result_after = register_symbol('internal.return_result_after')
break_loop = register_symbol('internal.break_loop')
leave_tokenizer_before = register_symbol('internal.leave_tokenizer_before')
leave_tokenizer_after = register_symbol('internal.leave_tokenizer_after')

TRANSPARENT_ACTION_SET = {no_action, skip, insert_blank_node}	#These are actions that are just relayed

class enter_sub_tokenizer_before(public_base):
	tokenizer = RTS.positional()
	pre_action = RTS.positional(default=None)
	post_action = RTS.positional(default=None)

class enter_sub_tokenizer_after(public_base):
	tokenizer = RTS.positional()
	pre_action = RTS.positional(default=None)
	post_action = RTS.positional(default=None)

class set_properties(public_base):
	data = RTS.all_named()

class return_value(public_base):
	value = RTS.positional()

class return_processed_match(public_base):
	#note - when we refer to processor we often will mean just a function that is meant to process something, but in other instances a processor may be an item processor or tree node processor.
	#		maybe we will adjust our glossary at some point to make it more clear what is what. I kinda liked filter but filter is already defined as conditional filtering in python.
	processor = RTS.positional()

class execute_node_body_in_context(public_base):
	context = RTS.positional()

class call_function_using_regex_match_as_arguments(public_base):
	function = RTS.positional()
	positional_processors = RTS.all_positional()
	named_processors = RTS.optional_factory(dict)	#We don't use RTS.all_named() because then we might interfere with function (we should keep this in mind in other places as well)
													#also note that we couldn't have additional features unless we did this, like additional_named
	additional_positional = RTS.optional_factory(tuple)
	additional_named = RTS.optional_factory(dict)


class call_function_with_regex_match(public_base):
	function = RTS.positional()
	additional_positional = RTS.optional_factory(tuple)
	additional_named = RTS.optional_factory(dict)

class call_function_with_regex_match_and_text(public_base):
	function = RTS.positional()
	additional_positional = RTS.optional_factory(tuple)
	additional_named = RTS.optional_factory(dict)

class call_function_with_node_and_regex_args(public_base):
	function = RTS.positional()
	additional_positional = RTS.optional_factory(tuple)
	additional_named = RTS.optional_factory(dict)

class call_function_with_processor_node_and_regex_match(public_base):
	function = RTS.positional()
	additional_positional = RTS.optional_factory(tuple)
	additional_named = RTS.optional_factory(dict)


class bind_and_call_function_with_processor_config_and_regex_args(public_base):
	function = RTS.positional()
	config = RTS.all_named()

class bind_and_call_function_with_processor_config_and_item(public_base):
	function = RTS.positional()
	config = RTS.all_named()

