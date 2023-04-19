#from ....rudimentary_types.context import context
from ....type_system.features import classmethod_with_specified_settings
from ....symbols import register_symbol
from .pp_bases import pp_action
import ast, sys
from .... import type_system as RTS
from ....type_system.bases import standard_base
from ....type_system import factory_self_reference as fsr
from .pp_structures import pp_ast_template
from ....data_utils import stack
from ....rudimentary_types.data_path import data_path

import textwrap, inspect,  functools

def indent(text, prefix='\t'):
	return textwrap.indent(textwrap.dedent(text).strip(), prefix)


#BUG - when updating linecache like this we will show the wrong source code if the error doesn't happen during the particular call, like if we define a function and that goes well but then we have an error when calling that function later on.
#		to solve this we should use the source tracker in deprecated module create_function

MISS = register_symbol('internal.miss')
RAISE_EXCEPTION = register_symbol('internal.raise_exception')

#import linecache

class context_accessor(standard_base):
	_context = RTS.field()

	def __getattr__(self, key):
		# ctx = self._context
		# if (value := ctx.locals.get(key, MISS)) is not MISS:
		# 	return value

		# if (value := ctx.globals.get(key, MISS)) is not MISS:
		# 	return value

		if (value := self._context.get(key, MISS)) is MISS:
			raise AttributeError(f'{self} have no local or global entry {key!r}.')
		else:
			return value

	def __setattr__(self, key, value):
		self._context.locals[key] = value


#NOTE - when not updating linecache, a previous execution that did may interfere with traceback, maybe we should change the default to do update?
#		or are there other ways to deal with this?

#TODO - move to somewhere else, doesn't have to be deep in here
class context(standard_base):
	locals = RTS.field(factory=dict)
	globals = RTS.field(**fsr, factory=lambda t: dict(t.builtins.__dict__))
	tracker = RTS.setting(None)
	#update_linecache = RTS.setting(False)
	parent = RTS.field(default=None)
	name = RTS.field(default=None)

	#TODO - settings here should be harmonized with the table processing stuff

	def get_by_data_path(self, p):
		p = data_path(p)
		ptr = self
		for part in p.parts:
			ptr = ptr.get(part)
		return ptr

	def get(self, key, default=RAISE_EXCEPTION):
		if (value := self.locals.get(key, MISS)) is not MISS:
			return value
		elif (value := self.globals.get(key, MISS)) is not MISS:
			return value
		elif default is RAISE_EXCEPTION:
			raise KeyError(f'{self} have no local or global entry {key!r}.')
		else:
			return default


	def update(self, other):
		self.locals.update(other.locals)
		self.globals.update(other.globals)

	def __repr__(self):
		return f'{self.__class__.__qualname__}({hex(id(self))} in `{self.qualified_name}´)'

	def set(self, name, value):
		self.locals[name] = value

	def set_and_return(self, name, value):
		self.locals[name] = value
		return value	#Allows inline expressions

	@property#TODO cached
	def accessor(self):
		return context_accessor(self)

	def stack(self, **named):
		return stack(self.locals, **named)

	__getitem__ = get
	__setitem__ = set

	@property
	def path(self):
		if self.name and self.parent:
			return f'{self.parent.path}.{self.name}'
		elif self.name:
			return self.name


	@property
	def qualified_name(self):
		if path := self.path:
			return path
		elif module := self.globals.get('__module__'):
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
	def selectively_create_from_this_frame(cls, *import_names, stack_offset=0):
		frame = sys._getframe(stack_offset + 1)

		pending_locals = dict()
		pending_globals = dict()

		for name in import_names:
			if (value := frame.f_locals.get(name, MISS)) is not MISS:
				pending_locals[name] = value

			if (value := frame.f_globals.get(name, MISS)) is not MISS:
				pending_globals[name] = value

		return cls(pending_locals, pending_globals)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_this_frame(cls, stack_offset=0, *, config):
		frame = sys._getframe(stack_offset + 2)	#NOTE - +2 because decorator adds one
		return cls._from_config(config, locals=frame.f_locals, globals=frame.f_globals)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_frame(cls, frame, *, config):
		return cls._from_config(config, locals=frame.f_locals, globals=frame.f_globals)


	#TODO - the four functions below needs to be harmonized and consolidated

	def eval_expression_dict(self, expression, stack_locals=None):	#This is useful in case stack_locals need to contain self or expression
		if self.tracker:
			file_info = self.tracker.register_new_file('expression', expression)
			code = compile(expression, file_info.file_id, 'eval')
		else:
			code = compile(expression, '<expression>', 'eval')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(code, self.globals, self.locals)
		else:
			return eval(code, self.globals, self.locals)


	def eval_expression(self, expression, **stack_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('expression', expression)
			code = compile(expression, file_info.file_id, 'eval')
		else:
			code = compile(expression, '<expression>', 'eval')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(code, self.globals, self.locals)
		else:
			return eval(code, self.globals, self.locals)

	def eval_expression_temporary_tracker(self, expression, **stack_locals):
		file_info = self.tracker.register_new_file('expression', expression)
		code = compile(expression, file_info.file_id, 'eval')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(code, self.globals, self.locals)
		else:
			return eval(code, self.globals, self.locals)

		file_info.purge()	#Expression is retained if an exception happens since then this statement is never reached - this is by design

	def exec_expression_dict(self, expression, stack_locals=None):	#This is useful in case stack_locals need to contain self or expression
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				exec(code, self.globals, self.locals)
		else:
			exec(code, self.globals, self.locals)

	def exec_expression(self, expression, **stack_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				exec(code, self.globals, self.locals)
		else:
			exec(code, self.globals, self.locals)

	def exec_expression_in_new_scope(self, expression, **additional_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		scope = additional_locals

		outer_scope = dict(self.globals)
		outer_scope.update(self.locals)

		exec(code, outer_scope, scope)
		return scope

	def create_bound_function(self, function, *additional_positional_arguments):
		arguments = (*self.locals.keys(), *additional_positional_arguments)
		assert len(set(arguments)) == len(arguments), f'Some arguments were specified twice: {arguments}'

		tree = ast.parse(inspect.getsource(function))
		function_body = ast.unparse(tree.body[0].body)
		arguments_def = ', '.join(arguments)
		python_code = (
			f'def {function.__name__}({arguments_def}):\n'
				f'{indent(function_body)}'
		)

		scope = self.exec_expression_in_new_scope(python_code)
		function = functools.partial(scope[function.__name__], *self.locals.values())

		return function


	def create_bound_function_from_snippet(self, snippet, *additional_positional_arguments, name='snippet'):
		arguments = (*self.locals.keys(), *additional_positional_arguments)
		assert len(set(arguments)) == len(arguments), f'Some arguments were specified twice: {arguments}'

		arguments_def = ', '.join(arguments)
		python_code = (
			f'def {name}({arguments_def}):\n'
				f'{indent(snippet)}'
		)

		scope = self.exec_expression_in_new_scope(python_code)
		return functools.partial(scope[name], *self.locals.values())





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




