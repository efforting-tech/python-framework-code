from .._mnemonic_bootstrap_layer.processor import Tree_Processor_Factory, Node_Handler_Description, Default_Handler
from .._mnemonic_bootstrap_layer import actions as MA
from .parser import parse_line
from .records import F_AST, CS_AST


F = Tree_Processor_Factory(ast_directory=F_AST.__dict__)
main = F.create_processor('main')


main.register(Node_Handler_Description(
	regex = '§(.*)',
	ast = 'statement',
	body = MA.Store_Node_As('body'),
	additional_factories = dict(
		title = lambda context: parse_line(context['result'].value.match.group(1), context['node']),
		source = lambda context: context['node'],
	),
))

main.register(Node_Handler_Description(
	pattern = Default_Handler,
	ast = 'node',
	body = MA.Store_Node_As('body', processor=main),
	additional_factories = dict(
		title = lambda context: parse_line(context['node'].title, context['node']),
		source = lambda context: context['node'],
	),
))



F2 = Tree_Processor_Factory()
template_statement_processor = F2.create_processor('template_statement_processor')
inline_expression_processor = F2.create_processor('inline_expression_processor')


template_statement_processor.register(Node_Handler_Description(
	pattern = 'Note[:]{anything as title}',
	ast = CS_AST.note,
	body = MA.Store_Node_As('body'),
	process_fields = dict(
		title = str.strip,
	),
	additional_factories = dict(
		source = lambda context: context['target']['source'],
	),
	bound = True,
))

template_statement_processor.register(Node_Handler_Description(
	pattern = 'Define Pythonic Inline Expression[:]{anything as pattern}',
	ast = CS_AST.define_pythonic_inline_expression,
	body = MA.Store_Node_As('body'),
	process_fields = dict(
		pattern = str.strip,
	),
	additional_factories = dict(
		source = lambda context: context['target']['source'],
	),
	bound = True,
))


inline_expression_processor.register(Node_Handler_Description(
	pattern = 'Note[:]{anything as title}',
	ast = CS_AST.inline_note,
	process_fields = dict(
		title = str.strip,
	),
	additional_factories = dict(
		source = lambda context: context['target']['parent'],
	),
	bound = True,
))




inline_expression_processor.register(Node_Handler_Description(
	pattern = Default_Handler,
	ast = CS_AST.unresolved_inline_expression,
	additional_factories = dict(
		source = lambda context: context['target']['parent'],
		expression = lambda context: context['result'].value.item,
	),
	bound = True,
))

