from ....improved_mnemonic_tree_processor.presets import main_processor
from ....resource_management import get_local_module_path
from ....text_nodes import text_node
from . import types as T
from .render import contextual_renderer
#template_body_processor = main_processor.context.require('template_body_processor')



template_processor_context = main_processor.context.advanced_sub_context(dict(T=T, text_node=text_node), name='template_processor_context')
main_processor.process_path(get_local_module_path('template_processor.treedef'), context=template_processor_context)
template_processor_context.export()



def load_template(source):
	#For now we assume source is a text_node

	ast_stack = list()
	ast_context = template_processor_context.sub_context(ast_stack=ast_stack)
	template_body_processor.process_tree(source, context=ast_context)
	t = T.template_sequence(ast_stack)
	return t
