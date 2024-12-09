from efforting.mvp6._template_bootstrap_layer.processor import main, inline_expression_processor, Node_Handler_Description
from efforting.mvp6._template_bootstrap_layer.context import template_implementation_context
from efforting.mvp6._template_bootstrap_layer.implementation import iteratively_implement_template
from efforting.mvp6.core.text import Immutable_Tree_View

#TODO - I think what we really need now is an improved tree view where we can also store information about spacing between nodes
#		Maybe we can render an Immutable_Tree_View into a better hierarchial variant specifically for source tracking




#TODO - We are currently mutating inline_expression_processor but we should probably be mutating a context instead and have the processors setup so that they will defer to the context for any non standard patterns.
#BUG - We are adding stuff after the catchall in inline_expression_processor

#BUG - next problem is the old problem with preserving blank spaces in nodes. We must investigate why this happens. If it is the Immutable_Tree_View or later.


from efforting.mvp6._template_bootstrap_layer.records import N_AST, CS_AST

from efforting.mvp6.core.data import Mutable_Basic_Record, Data_Stack

# r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

# 	This is a template.

# 	§ Note: This is a statement
# 		Part of statement

# 	§ This statement is «note: indirect»
# 		This is because it has expressions in its title
# 		But if we want «indirect» expressions inside the statement body the statement itself must support it.

# 	Here we have an «note: inline expression».
# 		Here is sub «note: stuff»!

# 	§ define pythonic inline expression: adjective
# 		import random
# 		return random.choice('stunning freaking interesting broken fascinating crazy insane'.split())

# 	§ define pythonic inline expression: capitalize[:] {anything}
# 		return anything.upper()

# 	§ define pythonic inline expression with context: if content[:] {anything}
# 		# This experiment accesses pending title. Anything is expected to be a python eval
# 		if context['pending_title']:
# 			return eval(anything)

# 	Experiments of «adjective» inline expressions both «capitalize: with» and without parameters



# 	Testing if content:
# 		«if content: ' → ' »A«if content: ' → ' »B
# 		A«if content: ' → ' »B


# '''))



source = Immutable_Tree_View.from_str('''

	A


''')
source.parent = source
r = main.dispatcher.dispatch_tree(source)


ctx = template_implementation_context()
res = tuple(iteratively_implement_template(ctx, r.value))

#res[-1].suffix_spacing = 1	#TODO - we are manually adding this now because we don't have a mechanism to calculate it yet

print(res[0].body)	#Why is body = ()



# EXPERIMENT

from efforting.mvp6.core import record as R

class abstract_template_renderer(R.Record):
	template: R.Field()
	context: R.Field(factory=Mutable_Basic_Record)

class immutable_text_tree_template_renderer(abstract_template_renderer):

	def _render_title(self, title):

		pending_result = list()

		def inner_render_title(item):
			match item:
				case (*list_of_sub_items,):
					#TODO - we may want result to be a mutable stack/list instead since we may want to have rendering operations that will be useful for joining items with separators or for removing trailing spaces.
					#for i in map(self._render_title, list_of_sub_items) if i is not None
					for sub_item in list_of_sub_items:
						inner_render_title(sub_item)

				case CS_AST.inline_note():
					pass

				case str():
					pending_result.append(item)

				case CS_AST.unresolved_inline_expression(expression=expression):
					#We will try to resolve this once
					match ctx.compile_expression(title, expression):
						case CS_AST.unresolved_inline_expression():
							raise Exception(f'Unable to resolve inline expression: {expression!r}')

						case unhandled:
							inner_render_title(unhandled)	#Defer to outer renderer

				case CS_AST.custom_inline_expression(function=function, parameters=parameters, additional_parameters=additional_parameters):
					ap = dict()
					for key, value in additional_parameters.items():
						match value:
							case 'context':
								ap[key] = dict(
									pending_title = pending_result,
								)
							case unhandled:
								raise Exception(value)

					if (value := function(*parameters, **ap)) is not None:
						pending_result.append(value)

				case unhandled:
					raise Exception(unhandled)

		inner_render_title(title)
		return ''.join(pending_result)



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

			case CS_AST.define_pythonic_inline_expression(pattern=pattern, body=body, settings=settings):

				additional_parameters = dict()
				additional_names = ()
				match settings:
					case 'context':
						additional_names = ('context',)
						additional_parameters['context'] = 'context'	#TODO maybe use symbols here or something

					case none if none is None:
						pass
					case unhandled:
						raise Exception(settings)

				def compile_function(context):
					field_names = [f.name for f in context['node_handler'].description.field_list]	#TODO- worry about duplicate names
					arguments = ', '.join((*field_names, *additional_names))
					result = Immutable_Tree_View.from_title_and_body(f'def pythonic_inline_expression({arguments}):', body.indented(normalized_indention=True))

					#TODO - support contexts and stuff
					scope = dict()
					code = compile(result.to_str(), '<pythonic_inline_expression>', 'exec')
					exec(code, scope)
					return scope['pythonic_inline_expression']

				inline_expression_processor.register(Node_Handler_Description(
					pattern = pattern,
					ast = CS_AST.custom_inline_expression,
					generate_field_list = True,
					additional_settings = dict(
						additional_parameters = additional_parameters,
					),
					additional_factories = dict(
						source = (lambda context: context['target']['parent']),
						function = compile_function,
						parameters = (lambda context: context['result'].value.match.groups()),
					),
					bound = True,
				))


			#case ():
			#	return Immutable_Tree_View.from_str('\n')

			case (*list_of_sub_items,):
				fragments = list()
				for sub_item in list_of_sub_items:
					fragments.extend('\n' for i in range(sub_item.prefix_spacing))
					if (sub_result := self._render_body(sub_item)) is not None:
						fragments.append(sub_result)
						fragments.extend('\n' for i in range(sub_item.suffix_spacing or 0))

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

#OUTPUT:

# indirect statement NOT IMPLEMENTED YET: title [' This statement is ', inline_note(source=statement(…) title='indirect' body=None)] body Immutable_Tree_View(lines=(Immutable_Line(text='\t\tThis is because it has expressions in its title'), Immutable_Line(text='\t\tBut if we want «indirect» expressions inside the statement body the statement itself must support it.')))
# --------------------
# This is a template.

# Here we have an .
#         Here is sub !

# Experiments of insane inline expressions both WITH and without parameters


