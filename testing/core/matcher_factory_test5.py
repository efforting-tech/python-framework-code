#Most recent note: This is starting to become a nice PoC for how we can bootstrap the template system. We should create a specific sub package for it.
#In matcher_factory_test6.py we should utilize the things moved to the proper place and at some point we should get back to actually creating maching factories.

#Yes - we are racking up quite a few of these experiments. Once the testing-directory goes into more of a unit testing type of direction this stuff will be cleaned up.
#Having it as different revisions is fine but then it becomes somewhat inconvenient to open the older versions with my current setup.

#This is based on matcher_factory_test3.py
#This one will focus on a simple template renderer before we address the remaining goals (from test3)
import re

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

F = Tree_Processor_Factory(ast_directory=dict(MI.implement_node_tree_iteratively(r.value)))
F_AST = type('AST', (), dict(F.ast_directory))


def parse_line(line, source=None):
	result = MT.template_tokenizer.tokenize(line, source=source)
	return result.tokens


# Next step is to process the parsed tree into an AST of parsed template features

s = MB.processor_def.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	create simple ast node tree:
		ast_node: source
			abstract_tree: title, body
				node
				indirect_statement

'''))


N_AST = type('N_AST', (), dict(MI.implement_node_tree_iteratively(s.value)))

s2 = MB.processor_def.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	create simple ast node tree:
		ast_node: source
			abstract_multiline_text: title, body
				note
				inline_note

'''))


CS_AST = type('CS_AST', (), dict(MI.implement_node_tree_iteratively(s2.value)))





def iteratively_implement_title(context, parent, item):
	match item:
		case [*list_of_items]:
			for sub_item in list_of_items:
				yield from iteratively_implement_title(context, parent, sub_item)

		case MT.Raw_Expression(rex):
			yield context.compile_expression(parent, rex.group(0))

		case MT.Text(re.Match() as match):
			yield match.group()

		case unmatched:
			raise Exception(type(item))

	yield from ()

#We might use a "manual" dispatcher here (match statement)
def iteratively_implement_template(context, item):
	match item:
		case [*list_of_items]:
			for sub_item in list_of_items:
				yield from iteratively_implement_template(context, sub_item)

		case F_AST.node(source, title, body):
			n_title = tuple(iteratively_implement_title(context, item, title))
			n_body = tuple(iteratively_implement_template(context, body))
			yield N_AST.node(item, n_title, n_body)

		case F_AST.statement(source, title, body):
			match tuple(iteratively_implement_title(context, item, title)):
				case [str(title_text)]:
					#print('STATEMENT TEXT', title_text)
					yield context.compile_statement(item, title_text, body)

				case [*list_of_items]:
					#One thing to consider here is that if the expression evaluates to a non indirect statement this statement could be treated like a direct one.
					#But we may still opt to not do that in order to allow it to be interpreted differently at some future point in a different context.
					#I guess this could be controlled by the context - we could have an optional optimization function we could call.
					yield N_AST.indirect_statement(item, list_of_items, body)

				case unmatched:
					raise Exception(unmatched)

		case unmatched:
			raise Exception(type(item))




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


class template_implementation_context:
	def compile_expression(self, parent, expression):
		return inline_expression_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			parent = parent,
		), Immutable_Tree_View.from_str(expression))

	def compile_statement(self, source, title, body):
		statement_node = Immutable_Tree_View.from_title_and_body(title, body.normal(1))
		return template_statement_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			source = source,
		), statement_node)

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


r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	This is a template.

	§ Note: This is a statement
		Part of statement

	§ This statement is «note: indirect»
		This is because it has expressions in its title
		But if we want «indirect» expressions inside the statement body the statement itself must support it.

	Here we have an «note: inline expression».
		Here is sub «note: stuff»!

'''))


ctx = template_implementation_context()
res = tuple(iteratively_implement_template(ctx, r.value))

from efforting.mvp6.template_system.introspection import Dumper
D = Dumper()
D.exlude_glob = (
	'*.source',
)

D.dump(res)	# https://gist.github.com/Mikael-Lovqvist/30f4944576b6fff4161f952059f67547
