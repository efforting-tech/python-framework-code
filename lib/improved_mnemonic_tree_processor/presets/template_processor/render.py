from . import types as T
from ....text_nodes import text_node
from .... import type_system as RTS
from ....type_system.bases import public_base
from ....data_utils import attribute_stack



class contextual_renderer(public_base):
	context = RTS.positional()
	templates = RTS.positional(factory=dict)

	def render_title_piece(self, piece):
		match piece:
			case str():
				return piece
			case T.placeholder(expression):
				return self.context.eval(expression)
			case _:
				raise TypeError(piece)

	def render_title(self, title):
		return ''.join(map(self.render_title_piece, title))


	def render_in_context(self, item, context):
		with attribute_stack(self, context=context):
			return self.render(item)

	def render_template(self, template, *positional, **named):
		if isinstance(template, str):
			template = self.templates[template]

		bound_arguments = template.signature.bind(*positional, **named)
		bound_arguments.apply_defaults()

		return self.render_in_context(template, self.context.advanced_sub_context(bound_arguments.arguments, name='template_with_signature_context'))

	def render(self, item):
		match item:
			case str():
				return self.render(self.templates[item])
			case T.sequence(sequence):
				result = text_node()
				for sub_item in sequence:
					result += self.render(sub_item)
				return result

			case T.meta_info(body=body):
				return self.render(body)

			case T.render_template_by_name(name):
				return self.render(self.templates[name])

			case T.execute(code):
				result = text_node()
				def emit(text):
					nonlocal result
					match text:
						case text_node():
							result += text
						case str():
							result.write(text)
						case _:
							raise TypeError(text)

				def emit_line(line):
					nonlocal result
					result.write(f'{line}\n')

				def emit_block(block):
					nonlocal result
					result += text_node.from_text(block)

				execute_context = self.context.advanced_sub_context(dict(emit=emit, emit_line=emit_line, emit_block=emit_block), name='execute_context')
				execute_context.exec(code)
				return result

			case T.call_function(function, signature):
				result = function(**{key:self.context.require(key) for key in signature.parameters})
				#Here we make sure to convert result to text_node but here we could do additional processing. TODO: Figure out if we want a generic post processing step to be added for the full set of features
				match result:
					case text_node():
						return result
					case str():
						return text_node.from_text(result)
					case _:
						raise TypeError(result)

			case T.unconditional(body):
				return self.render(body)

			case T.indented(body):
				return self.render(body).indented_copy()

			case T.conditional(expression, body, chain):
				if self.context.eval(expression):
					sub_renderer = contextual_renderer(self.context.sub_context(), self.templates)
					return sub_renderer.render(body)
				elif chain:
					return self.render(chain)
				else:
					return text_node()

			case T.for_loop(expression, body):	#TODO - this is silly, these functions should exist in execute contexts too
				result = text_node()
				def for_action():
					nonlocal result
					result += sub_renderer.render(body)

				def emit(text):
					nonlocal result
					match text:
						case text_node():
							result += text
						case str():
							result.write(text)
						case _:
							raise TypeError(text)

				def emit_line(line):
					nonlocal result
					result.write(f'{line}\n')

				def emit_block(block):
					nonlocal result
					result += text_node.from_text(block)

				for_context = self.context.advanced_sub_context(dict(__action__=for_action, emit=emit, emit_line=emit_line, emit_block=emit_block), name='for_context')
				sub_renderer = contextual_renderer(for_context, self.templates)
				for_context.exec(f'for {expression}:\n\t__action__()')


				return result

			case T.template_tree(title, branches):
				if title and branches:
					return text_node.from_title_and_body(self.render_title(title), self.render(branches))
				elif title:
					return text_node.from_text(self.render_title(title))
				elif branches:
					return text_node.from_branches(branches)
				else:
					return text_node()

			case _ if item is T.blank_line:
				return text_node.from_text('')

			case _ if item is None:
				return text_node()

			case  _:
				raise Exception(f'{item!r} could not be handled')