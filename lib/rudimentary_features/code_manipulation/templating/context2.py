from .pp_context import *
from ....type_system.bases import public_base

class context_dict_accessor(standard_base, dict):
	#TODO - ensure that all relevant functions are implemented!

	context = RTS.field()

	def __getitem__(self, key):
		if (value := self.context.get(key, MISS)) is MISS:
			raise AttributeError(f'{self} have no local or global entry {key!r}.')
		else:
			return value

	def __setitem__(self, key, value):
		self.context.locals[key] = value

#TODO - see /home/devilholk/Projects/graph_system_native/take2/t7b.py for imrovements regarding defining the local context for functions using closures
#ADDITIONAL:	By stacking the "outer" functions there we can create great cus0tom scoping!
#				we can also incorporate methods for merging multiple scopes if we want to support multiple parent scope, and then we may also need merge strategies defined

#TODO - move to string or text utils
import textwrap
def indented(text):
	return textwrap.indent(text, '\t')


#TODO move to data utils
from collections import Counter
def unique_names_from_generator(gen, prefill=None):
	seen = Counter()	#For initial count
	current_counter = Counter()	#For counting during name gen

	if prefill:
		seen.update(prefill)
		current_counter.update(prefill)

	names = tuple(gen)
	seen.update(names)
	result = list()
	mutation = False
	for n in names:
		count = seen[n]
		current = current_counter[n] = current_counter[n] + 1
		if count == 1:
			result.append(n)
		else:
			result.append(f'{n}_{current}')
			mutation = True

	if mutation:
		return unique_names_from_generator(result)	#Run again in case we had a conflict as we changed stuff
	else:
		return result


class context3(public_base):
	locals = RTS.positional(factory=dict)
	name = RTS.positional(default=None)
	parents = RTS.positional(default=())
	tracker = RTS.setting(None)


	@property
	def accessor(self):
		return context_accessor(self)

	@property
	def dict_accessor(self):
		return context_dict_accessor(self)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_this_frame(cls, stack_offset=0, name=None, *, config):
		frame = sys._getframe(stack_offset + 2)	#NOTE - +2 because decorator adds one
		#raise NotImplementedError("This feature is not implemented yet")	#TODO - make sure we create a proper context with the globals as an upper context

		root = cls._from_config(config, frame.f_globals, 'root')
		return root.sub_context(frame.f_locals, name)
		#return cls._from_config(config, **frame.f_locals)

	@classmethod
	def from_named(cls, name=None, /, **named):
		return cls(named, name)


	def stack(self, **named):	#This is a dict type stack operating on locals, is this what we want? Maybe we want a sub context?
		return stack(self.locals, **named)

	def sub_context(self, locals=None, name=None):
		if locals is None:		#A problem here is that factory will not be called because locals is None, we should use the undefined-symbol instead (TODO)
			locals = dict()
		child = self.__class__(locals, name, parents=(self,))
		return child

	def stacked_context(self, *pos, **locals):
		if pos:
			[name] = pos
			return self.sub_context(locals, name)
		else:
			return self.sub_context(locals)

	def eval_as_function(self, expression, **stack_locals):
		return self.exec_as_function(f'return {expression}', **stack_locals)

	def exec_as_function(self, statement, **stack_locals):
		if stack_locals:
			return self.sub_context(stack_locals).exec_as_function(statement)
		else:
			return self.create_function2(statement)()

	def exec_in_context(self, statement):
		#TODO - possible tracking
		exec(statement, self.dict_accessor, self.locals)

	def iter_ancestors(self):
		for parent in self.parents:
			yield from parent.iter_ancestors()
		yield self

	def iter_ancestors_reverse(self):
		yield self
		for parent in reversed(self.parents):
			yield from parent.iter_ancestors()

	def get_any_ancestral_tracker(self):
		for a in self.iter_ancestors():
			if a.tracker:
				return a.tracker

	def get_first(self, *keys):
		for k in keys:
			if value := self.get(k):
				return value

		for parent in self.parents:
			if value := parent.get_first(*keys):
				return value

	def set(self, key, value):
		self.locals[key] = value

	def require(self, key):
		if (value := self.get(key, MISS)) is MISS:
			raise Exception(f'{key!r} is not in {self}')
		return value

	def get(self, key, default=None):
		if (value := self.locals.get(key, MISS)) is not MISS:
			return value

		for parent in self.parents:
			if (value := parent.get(key, MISS)) is not MISS:
				return value

		return default

	def get_name(self):
		if self.name:
			return self.name
		elif name := self.get_first('name', '__name__'):
			return name
		else:
			return 'anonymous'

	def get_qualified_name_without_period(self):
		#Always uses first parent as primary (TODO - use first parent that is not anonymous)
		if self.parents:
			return f'{self.parents[0].get_name()}_{self.get_name()}'.replace('.', '_')
		else:
			return self.get_name().replace('.', '_')

	def update_from_frame(self, *names, stack_offset=0):
		frame = sys._getframe(1+stack_offset)
		for name in names:
			self.locals[name] = frame.f_locals[name]



	def create_function2(self, inner_body=None, inner_arguments='', inner_name='function', global_dict=None, creation_function_name = 'create_function'):	#TODO config?
		ancestors = tuple(self.iter_ancestors_reverse())

		prefill = set()
		for a in ancestors:
			prefill |= set(a.locals)

		names = unique_names_from_generator((a.get_qualified_name_without_period() for a in ancestors), prefill=prefill)

		seen = set()
		prepare = list()
		for n, a in zip(names, ancestors):
			for k in a.locals:
				if k not in seen:
					seen.add(k)
					prepare.append(f'{k} = {n}.locals[{k!r}]')


		prepare += [
			f'def {inner_name}({inner_arguments}):',
			indented(inner_body),
			f'return {inner_name}',
		]

		body = '\n'.join(prepare)
		creation_function_arguments = ', '.join(names)
		python_code = f'def {creation_function_name}({creation_function_arguments}):\n{indented(body)}'

		scope = dict()
		if tracker := self.get_any_ancestral_tracker():
			file_info = tracker.register_new_file('expression', python_code)
			code = compile(python_code, file_info.file_id, 'exec')
		else:
			code = compile(python_code, 'expression', 'exec')
		exec(code, scope, global_dict)
		return scope[creation_function_name](*ancestors)

	def create_function(self, inner_body, inner_arguments=''):
		raise Exception('deprecated')
		ancestors = tuple(self.iter_ancestors_reverse())

		prefill = set()
		for a in ancestors:
			prefill |= set(a.locals)

		names = unique_names_from_generator((a.get_qualified_name_without_period() for a in ancestors), prefill=prefill)
		creation_function_name = 'create_function'	#TODO config
		global_dict = None	#TODO config
		inner_name = 'inner'	#TODO config

		prefill |= set(names)

		#TODO - make sure we are not colliding with locals in any context!
		context_names = unique_names_from_generator((f'create_{n}' for n in names), prefill=prefill)
		current_body = f'def {inner_name}({inner_arguments}):\n{indented(inner_body)}'
		current_return = inner_name

		for cn, n, a in zip(context_names, names, ancestors):
			scope_prep = '\n'.join(f'{k} = {n}.locals[{k!r}]' for k in a.locals)
			current_body = f'{scope_prep}\ndef {cn}():\n{indented(current_body)}\n\treturn {current_return}'
			current_return = f'{cn}()'

		creation_function_arguments = ', '.join(names)

		python_code = f'def {creation_function_name}({creation_function_arguments}):\n{indented(current_body)}\n\treturn {current_return}'

		scope = dict()
		if tracker := self.get_any_ancestral_tracker():
			file_info = tracker.register_new_file('expression', python_code)
			code = compile(python_code, file_info.file_id, 'exec')
		else:
			code = compile(python_code, 'expression', 'exec')
		exec(code, scope, global_dict)
		return scope[creation_function_name](*ancestors)

		#TODO - future improvement
		#	Consider the following context
		#		p1 = context3(dict(stuff=123, thing='thing'), name='p1', tracker=tracker)
		#		p2 = context3(dict(stuff=456), name='p2')
		#		c2 = context3(dict(stuff=789), parents=(p1, p2), name='c2')

		#	Currently we would get the following function
		#		def create_function(p1_c2, p2, p1):
		#			stuff = p1.locals['stuff']
		#			thing = p1.locals['thing']
		#			def create_p1():
		#				stuff = p2.locals['stuff']
		#				def create_p2():
		#					stuff = p1_c2.locals['stuff']
		#					def create_p1_c2():
		#						def inner():
		#							return stuff, thing
		#						return inner
		#					return create_p1_c2()
		#				return create_p2()
		#			return create_p1()

		#	Which could be further boiled down to
		#		def create_function(p1_c2, p2, p1):
		#			stuff = p1.locals['stuff']
		#			thing = p1.locals['thing']
		#			stuff = p2.locals['stuff']
		#			stuff = p1_c2.locals['stuff']
		#			def inner():
		#				return stuff, thing
		#			return inner

		#	And this can even further be concensed into
		#		def create_function(p1_c2, p2, p1):
		#			thing = p1.locals['thing']
		#			stuff = p1_c2.locals['stuff']
		#			def inner():
		#				return stuff, thing
		#			return inner



#TODO - this is adapted from pp_context.context but not gone through properly
#TODO - maybe a lot of named args should not be double starred since it may interfere with other names and that could get confusing when using from_frame-methods
#TODO - also maybe parent should be a setting, and also tracker - we need to decide on this and create tests/docs
class context2(public_base):
	name = RTS.positional(default=None)
	locals = RTS.positional(factory=dict)
	parent = RTS.positional(default=None)
	tracker = RTS.setting(None)
	#update_linecache = RTS.setting(False)

	#TODO - settings here should be harmonized with the table processing stuff

	def iter_ancestors(self):
		if self.parent:
			yield from self.parent.iter_ancestors()
		yield self

	def create_globals(self):
		g = dict()
		for ctx in self.iter_ancestors():
			g.update(ctx.locals)

		return g

	def sub_context(self, name=None, locals=None):
		if locals is None:		#A problem here is that factory will not be called because locals is None, we should use the undefined-symbol instead (TODO)
			locals = dict()
		child = self.__class__(name, locals, self)
		child.tracker = self.tracker	#We copy the tracker reference but we should probably use a cached find-from-ancestor thing instead
		return child

	def get_by_data_path(self, p):
		p = data_path(p)
		ptr = self
		for part in p.parts:
			ptr = ptr.get(part)
		return ptr

	def get(self, key, default=RAISE_EXCEPTION):	#Maybe default should be none in line with dict.get?
		if (value := self.locals.get(key, MISS)) is not MISS:
			return value
		elif self.parent and (value := self.parent.get(key, MISS)) is not MISS:
			return value
		elif default is RAISE_EXCEPTION:
			raise KeyError(f'{self} have no local or ancestral entry {key!r}.')
		else:
			return default

	def update_from_frame(self, *names, stack_offset=0):
		frame = sys._getframe(1+stack_offset)
		for name in names:
			self.locals[name] = frame.f_locals[name]

	def update(self, other):
		self.locals.update(other.locals)

	def __repr__(self):
		return f'{self.__class__.__qualname__}({self.qualified_name})'

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
		if self.name and self.parent and (pp := self.parent.path):
			return f'{pp}.{self.name}'
		elif self.name:
			return self.name

	@property
	def qualified_name(self):
		if path := self.path:
			return path
		elif cq := self.container_qualified_name:
			return f'{hex(id(self))} in `{cq}´'
		else:
			return f'{hex(id(self))}'

	@property
	def container_qualified_name(self):
		if (module := self.get('__module__', None)):
			if name := self.get('__qualname__', None):
				return f'{module}.{name}'
			elif name := self.get('__name__', None):
				return f'{module}.{name}'
			elif name := self.get('name', None):
				return f'{module}.{name}'
			else:
				return f'{module}'

		elif name := self.get('__qualname__', None):
			return f'{name}'
		elif name := self.get('__name__', None):
			return f'{name}'
		elif name := self.get('name', None):
			return f'{name}'


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

		raise NotImplementedError("This feature is not implemented yet")	#TODO - make sure we create a proper context with the globals as an upper context
		return cls(pending_locals, pending_globals)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_this_frame(cls, stack_offset=0, name=None, *, config):
		frame = sys._getframe(stack_offset + 2)	#NOTE - +2 because decorator adds one
		#raise NotImplementedError("This feature is not implemented yet")	#TODO - make sure we create a proper context with the globals as an upper context

		root = cls._from_config(config, frame.f_globals)
		return root.sub_context(name, frame.f_locals)
		#return cls._from_config(config, **frame.f_locals)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_frame(cls, frame, *, config):
		raise NotImplementedError("This feature is not implemented yet")	#TODO - make sure we create a proper context with the globals as an upper context
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
				return eval(code, self.create_globals(), self.locals)
		else:
			return eval(code, self.create_globals(), self.locals)


	def eval_expression(self, expression, **stack_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('expression', expression)
			code = compile(expression, file_info.file_id, 'eval')
		else:
			code = compile(expression, '<expression>', 'eval')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(code, self.create_globals(), self.locals)
		else:
			return eval(code, self.create_globals(), self.locals)

	def eval_expression_temporary_tracker(self, expression, **stack_locals):
		file_info = self.tracker.register_new_file('expression', expression)
		code = compile(expression, file_info.file_id, 'eval')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				return eval(code, self.create_globals(), self.locals)
		else:
			return eval(code, self.create_globals(), self.locals)

		file_info.purge()	#Expression is retained if an exception happens since then this statement is never reached - this is by design

	def exec_expression_dict(self, expression, stack_locals=None):	#This is useful in case stack_locals need to contain self or expression
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				exec(code, self.create_globals(), self.locals)
		else:
			exec(code, self.create_globals(), self.locals)

	def exec_expression(self, expression, **stack_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		if stack_locals:
			with stack(self.locals, stack_locals) as frame:
				exec(code, self.create_globals(), self.locals)
		else:
			exec(code, self.create_globals(), self.locals)

	def exec_expression_in_new_scope(self, expression, **additional_locals):
		if self.tracker:
			file_info = self.tracker.register_new_file('statement', expression)
			code = compile(expression, file_info.file_id, 'exec')
		else:
			code = compile(expression, '<statement>', 'exec')

		scope = additional_locals

		outer_scope = self.create_globals()
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


	def create_bound_function_from_snippet(self, snippet, *additional_positional_arguments, name='snippet', allow_clobbering=False):
		#We introduced allow_clobbering to help with when nested functions are created and the locals already contains stuff we override
		#but I don't think I really like that we build a function like this anyway, maybe we could find a better way
		#the main problem is to create a function that has a specific local predefined scope at compile time
		#it becomes a bit horrid with stuff like .. snippet() takes 35 positional arguments but 38 were given


		if allow_clobbering:
			apa_set = set(additional_positional_arguments)
			pending_locals = {k: v for k, v in self.locals.items() if k not in apa_set}
		else:
			pending_locals = self.locals

		arguments = (*pending_locals.keys(), *additional_positional_arguments)
		assert len(set(arguments)) == len(arguments), f'Some arguments were specified twice: {arguments}'

		arguments_def = ', '.join(arguments)
		python_code = (
			f'def {name}({arguments_def}):\n'
				f'{indent(snippet)}'
		)

		scope = self.exec_expression_in_new_scope(python_code)
		return functools.partial(scope[name], *pending_locals.values())





	#For now we define this but a subclass would currently overwrite it rather than extend it
	class builtins:
		pass

