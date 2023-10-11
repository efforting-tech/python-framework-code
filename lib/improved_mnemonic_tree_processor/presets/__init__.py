from ..tree_node_processing import improved_text_node_processor
from .. import create_tree_processor_rule_for_mnemonic, create_tree_processor_rule_for_regex, create_tree_processor_rule_for_literal, set_tree_processor_default_rule
from ...improved_text_processor import improved_text_processor
from ...improved_text_processor import create_text_processor_rule_for_mnemonic, create_text_processor_rule_for_regex, create_text_processor_rule_for_literal, set_text_processor_default_rule
from ...resource_management import get_resource_path


from ..context import context
from .. import conditions as C
from .. import actions as A




define_tree_processor = improved_text_node_processor(name='define_tree_processor')
define_tree_processor.add_rule(C.title_condition(C.matches_mnemonic('mnemonic[:] {mnemonic...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_tree_processor_rule_for_mnemonic))
define_tree_processor.add_rule(C.title_condition(C.matches_mnemonic('regex[:] {pattern...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_tree_processor_rule_for_regex))
define_tree_processor.add_rule(C.title_condition(C.matches_mnemonic('literal[:] {pattern...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_tree_processor_rule_for_literal))
define_tree_processor.add_rule(C.title_condition(C.matches_mnemonic('default[:]')), A.bind_and_call_function_with_processor_config_and_regex_args(set_tree_processor_default_rule))

define_text_processor = improved_text_node_processor(name='define_text_processor')
define_text_processor.add_rule(C.title_condition(C.matches_mnemonic('mnemonic[:] {mnemonic...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_text_processor_rule_for_mnemonic))
define_text_processor.add_rule(C.title_condition(C.matches_mnemonic('regex[:] {pattern...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_text_processor_rule_for_regex))
define_text_processor.add_rule(C.title_condition(C.matches_mnemonic('literal[:] {pattern...}')), A.bind_and_call_function_with_processor_config_and_regex_args(create_text_processor_rule_for_literal))
define_text_processor.add_rule(C.title_condition(C.matches_mnemonic('default[:]')), A.bind_and_call_function_with_processor_config_and_regex_args(set_text_processor_default_rule))



main_processor = improved_text_node_processor(name='main_processor', context=context(dict(
	define_tree_processor=define_tree_processor,
	improved_text_node_processor=improved_text_node_processor,
	define_text_processor=define_text_processor,
	improved_text_processor=improved_text_processor
), name='main'))

main_processor.context.update(main_processor=main_processor)

main_processor.context.update(__package__=__package__, __name__=__name__, __path__=__path__, __file__=__file__, __spec__=__spec__)

define_tree_processor.process_text('''

	mnemonic: tree processor[:] {name...}
		ctx = config.context
		new_processor = improved_text_node_processor(name=name, context=ctx)
		define_tree_processor.process_tree(node.body, context=ctx.sub_context(target_processor=new_processor))
		ctx.set(name, new_processor)

	mnemonic: text processor[:] {name...}
		ctx = config.context
		new_processor = improved_text_processor(name=name, context=ctx)
		define_text_processor.process_tree(node.body, context=ctx.sub_context(target_processor=new_processor))
		ctx.set(name, new_processor)

	mnemonic: amend processor[:]
		ctx = config.context
		define_tree_processor.process_tree(node.body, context=ctx.sub_context(target_processor=processor))

	mnemonic: amend processor[:] {name...}
		ctx = config.context
		define_tree_processor.process_tree(node.body, context=ctx.sub_context(target_processor=ctx.require(name)))

''', context=main_processor.context.sub_context(target_processor=main_processor))

main_processor.process_path('bootstrap.treedef', workdir=get_resource_path('improved_mnemonic_tree_processing'))
