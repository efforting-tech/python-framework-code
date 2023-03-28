#from ....rudimentary_types.context import context
from .pp_bases import pp_action
import ast, sys
from .... import rudimentary_type_system as RTS
from ....rudimentary_type_system.bases import standard_base
from ....rudimentary_type_system import factory_self_reference as fsr
from .pp_structures import pp_ast_template
from ....data_utils import stack


MISS = object()	#TODO symbol

import linecache

#TODO - classmethods with settings system

#TODO - move to somewhere else, doesn't have to be deep in here
class context(standard_base):
	locals = RTS.field(factory=dict)
	globals = RTS.field(**fsr, factory=lambda t: dict(t.builtins.__dict__))
	update_linecache = RTS.setting(False)

	#TODO - settings here should be harmonized with the table processing stuff

	def update(self, other):
		self.locals.update(other.locals)
		self.globals.update(other.globals)

	def __repr__(self):
		return f'{self.__class__.__qualname__}({hex(id(self))} in `{self.qualified_name}´)'


	@property
	def qualified_name(self):
		if module := self.globals.get('__module__'):
			if name := self.globals.get('__name__'):
				return f'{module}.{name}'
			elif name := self.globals.get('name'):
				return f'{module}.{name}'
			else:
				return f'{module}'

		elif name := self.globals.get('__name__'):
			return f'{name}'
		elif name := self.globals.get('name'):
			return f'{name}'
		else:
			return ''


	@classmethod
	def selectively_create_from_this_frame(cls, *import_names, stack_offset=0, update_linecache=False):
		frame = sys._getframe(stack_offset + 1)

		pending_locals = dict()
		pending_globals = dict()

		for name in import_names:
			if (value := frame.f_locals.get(name, MISS)) is not MISS:
				pending_locals[name] = value

			if (value := frame.f_globals.get(name, MISS)) is not MISS:
				pending_globals[name] = value

		return cls(pending_locals, pending_globals, update_linecache=update_linecache)

	@classmethod
	def from_this_frame(cls, stack_offset=0, update_linecache=False):
		frame = sys._getframe(stack_offset + 1)
		return cls(frame.f_locals, frame.f_globals, update_linecache=update_linecache)

	@classmethod
	def from_frame(cls, frame, update_linecache=False):
		return cls(frame.f_locals, frame.f_globals, update_linecache=update_linecache)


	def eval_expression_dict(self, expression, stack_locals=None):	#This is useful in case stack_locals need to contain self or expression
		if self.update_linecache:
			previous_cache = linecache.cache.get('<string>')
			linecache.cache['<string>'] = (len(expression), None, expression.split('\n'), '<string>')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(expression, self.globals, self.locals)
		else:
			return eval(expression, self.globals, self.locals)

		if self.update_linecache:
			if previous_cache is None:
				linecache.cache.pop('<string>')
			else:
				linecache.cache['<string>'] = previous_cache

	def eval_expression(self, expression, **stack_locals):
		if self.update_linecache:
			previous_cache = linecache.cache.get('<string>')
			linecache.cache['<string>'] = (len(expression), None, expression.split('\n'), '<string>')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(expression, self.globals, self.locals)
		else:
			return eval(expression, self.globals, self.locals)

		if self.update_linecache:
			if previous_cache is None:
				linecache.cache.pop('<string>')
			else:
				linecache.cache['<string>'] = previous_cache


	#For now we define this but a subclass would currently overwrite it rather than extend it
	class builtins:
		pass


class template_pp_context(context):

	class builtins:
		class create_template(pp_action):
			name = RTS.positional()
			replacements = RTS.all_positional()

			def process_command(self, processor, command, node):
				processor.context.locals[self.name] = pp_ast_template(self.name, self.replacements, ast.parse(node.text)).prepare


		class concat(pp_action):
			value = RTS.positional()

			def process_command(self, processor, command, node):
				assert not node.has_contents	#This command may not have a body (might have in the future, we will see)

				#TODO - maybe we need to be able to acquire the target AST from different types, now we are assuming we can just render it
				#		but value might already be rendered or maybe it is a string, who knows!

				#Currently we will support If only
				if isinstance(processor.previous_sibling, ast.If):
					processor.previous_sibling.orelse.extend(self.value.render(processor))
				else:
					raise Exception(processor.previous_sibling, self.value)
