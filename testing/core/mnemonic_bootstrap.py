from mnemonic_processor import Tree_Processor_Factory, Node_Handler_Description
from efforting.mvp6.data_utils import csloi
import mnemonic_actions as MA, mnemonic_handlers as MH

#Bootstrap factory
BSF = Tree_Processor_Factory()
processor_def = BSF.create_processor('processor_def')
simple_ast_node_processor = BSF.create_processor('simple_ast_node_processor')
simple_symbol_processor = BSF.create_processor('simple_symbol_processor')

simple_ast_node_tree = BSF.create_simple_ast_node('simple_ast_node_tree', 'members')
simple_ast_type = BSF.create_simple_ast_node('simple_ast_type', 'name', 'members', 'children')
simple_ast_symbols = BSF.create_simple_ast_node('simple_ast_symbols', 'members')
symbol = BSF.create_simple_ast_node('symbol', 'name')

simple_ast_node_processor.register(Node_Handler_Description(
	pattern = '{name}[:]',
	ast = simple_ast_type,
	body = MA.Store_Node_As('children', processor=simple_ast_node_processor),
	process_fields = dict(
		members = csloi,
	),
))

simple_ast_node_processor.register(Node_Handler_Description(
	pattern = '{name}[:]{text as members}',
	ast = simple_ast_type,
	body = MA.Store_Node_As('children', processor=simple_ast_node_processor),
	process_fields = dict(
		members = csloi,
	),
))


simple_symbol_processor.register(Node_Handler_Description(
	pattern = '{name}',
	ast = symbol,
))

MH.register_terminal_sub_handler(processor_def, simple_ast_node_tree, simple_ast_node_processor, 'Create Simple AST Node Tree', body_name='members')
MH.register_terminal_sub_handler(processor_def, simple_ast_symbols, simple_symbol_processor, 'Create Symbols', body_name='members')
