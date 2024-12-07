from efforting.mvp6._template_bootstrap_layer.processor import main
from efforting.mvp6._template_bootstrap_layer.context import template_implementation_context
from efforting.mvp6._template_bootstrap_layer.implementation import iteratively_implement_template
from efforting.mvp6.core.text import Immutable_Tree_View

from efforting.mvp6._template_bootstrap_layer.records import N_AST, CS_AST

from efforting.mvp6.core.data import Mutable_Basic_Record, Data_Stack

r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	This is a template.

	§ Note: This is a statement
		Part of statement

	§ This statement is «note: indirect»
		This is because it has expressions in its title
		But if we want «indirect» expressions inside the statement body the statement itself must support it.

	Here we have an «note: inline expression».
		Here is sub «note: stuff»!

	More Stuff

'''))


ctx = template_implementation_context()
res = tuple(iteratively_implement_template(ctx, r.value))





# EXPERIMENT

from efforting.mvp6.core import record as R

class abstract_template_renderer(R.Record):
	template: R.Field()
	context: R.Field(factory=Mutable_Basic_Record)

class immutable_text_tree_template_renderer(abstract_template_renderer):

	def _render_title(self, title):
		match title:
			case (*list_of_sub_items,):
				#TODO - we may want result to be a mutable stack/list instead since we may want to have rendering operations that will be useful for joining items with separators or for removing trailing spaces.
				result = tuple(i for i in map(self._render_title, list_of_sub_items) if i is not None)
				return ''.join(result)

			case str():
				return title

			case CS_AST.inline_note():
				pass

			case unhandled:
				raise Exception(unhandled)

	def _render_body(self, item):
		match item:
			case N_AST.node(title=title, body=body):
				#print('node:', 'title', title, 'body', body)
				rendered_title = self._render_title(title)
				rendered_body = self._render_body(body)
				#print('node:', 'rendered_title', rendered_title, 'rendered_body', rendered_body)
				return Immutable_Tree_View.from_title_and_body(rendered_title, rendered_body.indented(normalized_indention=True))

			case N_AST.indirect_statement(title=title, body=body):
				print('indirect statement NOT IMPLEMENTED YET:', 'title', title, 'body', body)

			case CS_AST.note():
				pass

			case ():
				return Immutable_Tree_View.from_str('\n')

			case (*list_of_sub_items,):
				fragments = tuple(i for i in map(self._render_body, list_of_sub_items) if i is not None)
				return Immutable_Tree_View.from_fragments(fragments)


			case unhandled:
				raise Exception(unhandled)


	def render(self, **contextual_updates):
		with Data_Stack(self.context, contextual_updates):
			return self._render_body(self.template)

tr = immutable_text_tree_template_renderer(res)
result = tr.render()
print('-'*20)
print(result.to_str())