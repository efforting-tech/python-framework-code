#This is based on matcher_factory_test3.py
#This one will focus on a simple template renderer before we address the remaining goals (from test3)

from efforting.mvp6.core.text import Immutable_Tree_View
from mnemonic_processor import Tree_Processor_Factory, Node_Handler_Description, Default_Handler
import mnemonic_implementation as MI, mnemonic_bootstrap as MB, mnemonic_actions as MA, mnemonic_tokenizer as MT

r = MB.processor_def.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''


	create simple ast node tree:
		abstract_node: source
			text: content

			abstract_tree: title, body
				node
				statement

			inline_expression: expression

'''))

def parse_line(line, source=None):
	result = MT.template_tokenizer.tokenize(line, source=source)
	return result.tokens



F = Tree_Processor_Factory(ast_directory=dict(MI.implement_node_tree_iteratively(r.value)))
main = F.create_processor('main')


main.register(Node_Handler_Description(
	regex = f'§(.*)',
	ast = 'statement',
	body = MA.Store_Node_As('body'),
	additional_factories = dict(
		title = lambda context: parse_line(context['node'].title, context['node']),
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


r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	This is a template.
	§ This is a statement
		Part of statement
	Here we have an «inline expression».
		Here is sub «stuff»!

'''))


#Now we have a tree - let's dump it
from efforting.mvp6.template_system.introspection import Dumper
Dumper().dump(r.value)


#OUTPUT:

# list
#   [0] mnemonic_implementation.node:
#     source: efforting.mvp6.core.text.Immutable_Tree_View
#       'This is a template.'
#     title: list
#       [0] mnemonic_tokenizer.Text:
#         match: Match: <re.Match object; span=(0, 19), match='This is a template.'>
#     body: efforting.mvp6.core.text.Immutable_Tree_View
#   [1] mnemonic_implementation.statement:
#     source: efforting.mvp6.core.text.Immutable_Tree_View
#       '§ This is a statement'
#       '\tPart of statement'
#     title: list
#       [0] mnemonic_tokenizer.Text:
#         match: Match: <re.Match object; span=(0, 21), match='§ This is a statement'>
#     body: efforting.mvp6.core.text.Immutable_Tree_View
#       '\tPart of statement'
#   [2] mnemonic_implementation.node:
#     source: efforting.mvp6.core.text.Immutable_Tree_View
#       'Here we have an «inline expression».'
#       ''
#     title: list
#       [0] mnemonic_tokenizer.Text:
#         match: Match: <re.Match object; span=(0, 16), match='Here we have an '>
#       [1] mnemonic_tokenizer.Raw_Expression:
#         match: Match: <re.Match object; span=(17, 34), match='inline expression'>
#       [2] mnemonic_tokenizer.Text:
#         match: Match: <re.Match object; span=(35, 36), match='.'>
#     body: efforting.mvp6.core.text.Immutable_Tree_View
#       ''
