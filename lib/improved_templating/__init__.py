from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_nodes import text_node
from ..improved_tokenizer import improved_tokenizer
from ..improved_mnemonic_tree_processor import actions as A
from ..improved_mnemonic_tree_processor import conditions as C
from ..improved_mnemonic_tree_processor.context import context as context_type

class switch(public_base):
	expression = RTS.positional()
	branches = RTS.factory(list)

class for_loop(public_base):
	expression = RTS.positional()
	sub_template = RTS.positional()

class conditional(public_base):
	expression = RTS.positional()
	sub_template = RTS.positional()

class indented(public_base):
	sub_template = RTS.positional()

class insert_body(public_base):
	body = RTS.positional()

class conditional_else(public_base):
	sub_template = RTS.positional()

class switch_branch(public_base):
	expression = RTS.positional()
	sub_template = RTS.positional()

class template_tree(public_base):
	title = RTS.positional(default=None)
	children = RTS.positional(factory=list)

class placeholder(public_base):
	name = RTS.positional()

	@classmethod
	def from_match(cls, match):
		return cls(match.group(1).strip())

#Tokenizer should only be used when defining templates since otherwise we may evaluate multiple times which can cause issues
template_tokenizer = improved_tokenizer(name='template_tokenizer')
template_tokenizer.add_rule(C.matches_regex(r'\\«'), A.return_value('«'))
template_tokenizer.add_rule(C.matches_regex(r'\\»'), A.return_value('»'))
template_tokenizer.add_rule(C.matches_regex(r'«(.*?)»'), A.return_processed_match(placeholder.from_match))
template_tokenizer.default_action = A.return_processed_match(lambda match: match.group())



#TODO: In order to implement "if - else" we need to render sequences so we can look at the previous value. We also need to cache the result of any evaluated expression.
#		this means we need to convert a bunch of list comprehensions to actually call a helper function. We also do have quite a lot of overlap here with common code
#		so this module could need a lot of clean up

class code_template(public_base):
	name = RTS.positional(default=None)
	contents = RTS.positional(factory=template_tree)
	context = RTS.positional(default=None)


	@classmethod
	def from_definition(cls, contents, name=None, context=None):
		from ..improved_mnemonic_tree_processor import presets as IMTPP
		template_body_processor = IMTPP.main_processor.context.accessor.template_body_processor
		ctx = context or IMTPP.main_processor.context

		result = cls(name, None, ctx)
		result.contents = tuple(template_body_processor.process_tree(contents, include_blanks=True, context=ctx.sub_context(target_template=result)))
		return result

	def maybe_render(self, context=None):
		if context is None:
			context = self.context

		def _resolve(item):	#Maybe resolve
			match item:
				case placeholder(name):

					if name.isidentifier():
						if (result := context.get(name)) is not None:
							return _resolve(result)
						else:
							return item
					else:
						try:
							return context.eval(name)	#Should we strictly require evaluation? Or should we be ok with anything not NameError
						except NameError:
							return item

				case str():
					return item

				#case int() | float():	#TODO - what else? anything?

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')




		def _render_line(line):
			match line:
				case str():
					return line# _render_line(template_tokenizer.process_text(line).tokens)

				case None:
					return ()

				case tuple() | list():
					pending = tuple(map(_resolve, line))
					if all(isinstance(i, str) for i in pending):
						return ''.join(pending)
					else:
						return pending

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _render(item):
			#print('RENDER', repr(item))
			match item:
				case tuple() | list():
					body = tuple(map(_render, item))
					if all(isinstance(i, text_node) for i in body):
						return text_node.from_branches(*body)
					else:
						return template_tree(None, body)

				case str():
					line = _render_line(item)
					if isinstance(line, str):
						return text_node.from_text(line)
					else:
						return template_tree(line, ())

				case template_tree():
					line = _render_line(item.title)
					body = tuple(map(_render, item.children))
					if isinstance(line, str) and all(isinstance(i, text_node) for i in body):
						return text_node.from_title_and_branches(line, tuple(map(_render, item.children)))
					else:
						return template_tree(line, body)

				case A.skip:
					return item

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		return _render(self.contents)

	def render(self, context=None, body=None, **updates):
		if context is None:
			context = self.context or context_type()

		if updates:
			context = context.sub_context(**updates)


		def _resolve_tn(item):	#Strict resolve text node
			match item:
				case text_node():
					return item

				case str():
					return text_node.from_text(item)


				case template_tree():
					return _render(item)

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _resolve(item):	#Strict resolve
			match item:
				case placeholder(name):
					try:
						if name.isidentifier():
							return _resolve(context.require(name))
						else:
							result = _resolve_tn(context.eval(name))
							if len(result.lines) == 1:
								return result.lines[0]
							else:
								return result
					except Exception as e:
						raise Exception(f'Placeholder {item} could not be resolved because of: {e}') from e

				case template_tree():
					return _render(item)


				case tuple() | list():
					return text_node.from_branches(*map(_resolve_tn, item))
					#return text_node(item)

				case text_node() | str():
					return item


				#case int() | float():	#TODO - what else? anything?

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _render_line(line):
			match line:
				case str():
					return line# _render_line(template_tokenizer.process_text(line).tokens)

				case (placeholder() as ph,):
					return _resolve(ph)

				case tuple() | list():
					pending = map(_resolve, line)
					return ''.join(map(str, pending))

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _render(item):
			match item:
				case tuple() | list():
					return text_node.from_branches(*(i for i in map(_render, item) if i is not A.skip))

				case str():
					return text_node.from_text(_render_line(item))

				case A.skip:
					return A.skip

				case text_node():
					return item

				case template_tree():
					if item.title is None:
						return text_node.from_branches(*map(_render, (i for i in item.children if i is not A.skip)))
					else:
						title_or_text_node = _render_line(item.title)
						if isinstance(title_or_text_node, text_node):
							assert not item.children
							return title_or_text_node
						else:
							return text_node.from_title_and_branches(title_or_text_node, tuple(map(_render, (i for i in item.children if i is not A.skip))))

				case conditional(expression, sub_template):
					if context.eval(expression):
						return _render(sub_template)
					else:
						return A.skip

				case switch(expression, branches=branches):
					ex = context.eval(expression)
					for b in branches:
						if context.eval(b.expression) == ex:
							return b.sub_template


					raise Exception('Switch')	#TODO - strict/unstrict/default



				case for_loop(expression, sub_template):
					render_context = context.sub_context()
					result = list()
					def process():
						result.append(sub_template.render(render_context))

					render_context.update(_process = process)
					render_context.exec(f'for {expression}:\n\t_process()')

					return text_node.from_branches(*result)

				case indented():
					return _render(item.sub_template).indented_copy()

				case insert_body():
					return context.accessor.__node__.body.dedented_copy()

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')




		return _render(self.contents)



	def preview(self):

		def _resolve(item):	#Maybe resolve
			match item:
				case placeholder(name):

					return f'« {name} »'

				case str():
					return item

				#case int() | float():	#TODO - what else? anything?

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _render_line(line):
			match line:
				case str():
					return line# _render_line(template_tokenizer.process_text(line).tokens)

				case tuple() | list():
					pending = map(_resolve, line)
					return ''.join(map(str, pending))

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		def _preview(item):
			match item:
				case tuple() | list():
					return text_node.from_branches(*map(_preview, item))

				case str():
					return text_node.from_text(_render_line(item))

				case text_node():
					return item

				case template_tree():
					if item.title is None:
						return text_node.from_branches(*map(_preview, (i for i in item.children if i is not A.skip)))
					else:
						return text_node.from_title_and_branches(_render_line(item.title), tuple(map(_preview, (i for i in item.children if i is not A.skip))))

				case switch():
					return text_node.from_text(f'§ switch {item.expression} ...')

				case conditional():
					return text_node.from_title_and_body(f'§ if {item.expression}', _preview(item.sub_template))

				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')




		return _preview(self.contents)


