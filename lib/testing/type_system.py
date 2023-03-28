import sys, textwrap


def indent(text, prefix='\t'):
	return textwrap.indent(textwrap.dedent(text).strip(), prefix)

class pending_stackable_dict_state_application:
	def __init__(self, target, state):
		self.target = target
		self.state = state
		self.previous = None

	def __enter__(self):
		assert self.previous is None

		self.previous = dict()
		for key, value in self.state.items():
			self.previous[key] = self.target.get(key, MISS)
			self.target[key] = value


	def __exit__(self, et, ev, tb):
		for key, value in self.previous.items():
			if value is MISS:
				selt.target.pop(key)
			else:
				self.target[key] = value

		self.previous = None

class prepared_stackable_dict_state:
	def __init__(self, state=None):
		if state is not None:
			self.state = state
		else:
			self.state = dict()

	def __setitem__(self, key, value):
		self.state[key] = value

	def __getitem__(self, key):
		return self.state[key]

	def get(self, key, default=None):
		return self.state.get(key, default)

	def __call__(self, target_dict):
		return pending_stackable_dict_state_application(target_dict, self.state)



def dict_merge_last_priority(*source_list):
	result = dict()
	for source in source_list:
		result.update(source)
	return result
def create_function(name, arguments, body, globals=None, locals=None, constants=None, stack_offset=0, source_tracking=None, source_update=(), filename=None, ast_preprocessor=None, ast_postprocessor=None, global_stack_data=None):
	frame = sys._getframe(1 + stack_offset)

	python_code = (
		f'def {name}({arguments}):\n'
			f'{indent(body)}'
	)

	ls = dict()
	if locals:
		ls.update(locals)

	if source_tracking:
		#Note, in the future there may be ways to watch for new code objects: https://github.com/python/cpython/blob/f07daaf4f7a637f9f9324e7c8bf78e8a3faae7e0/Objects/codeobject.c#L421

		file_info = source_tracking.register_new_file(filename)
		filename = file_info.file_id
	else:
		file_info = None
		filename = f'<function `{name}´>'

	if constants or ast_preprocessor or ast_postprocessor:
		pending_tree = ast.parse(python_code)

		if ast_preprocessor:
			pending_tree = ast_preprocessor(pending_tree)

		if constants:
			final_tree, reverse_mapping_index = ast_replace_constants_and_return_mapping(pending_tree, constants)
		else:
			final_tree, reverse_mapping_index = pending_tree, None

		if ast_postprocessor:
			final_tree = ast_postprocessor(final_tree)

		final_code = ast.unparse(final_tree)

		if source_tracking:	#Hack to make sure the tree really matches the code - possibly there are better ways to do this
			final_tree = ast.parse(final_code)

		code = compile(final_tree, filename, 'exec')
	else:
		final_tree, reverse_mapping_index = None, None
		final_code = python_code
		code = compile(python_code, filename, 'exec')

	if globals is None:
		globals = frame.f_globals

	g_stack = prepared_stackable_dict_state(global_stack_data)
	with g_stack(globals):
		exec(code, globals, ls)

	function = ls[name]

	if reverse_mapping_index:
		function_replace_string_constants_using_lut(function, reverse_mapping_index)

	if file_info:
		file_info.update(
			arguments = arguments,
			body = body,
			code = code,
			constants = constants,
			final_tree = final_tree,
			source_code = final_code,
			globals = globals,
			locals = locals,
			name = name,
			python_code = python_code,
			reverse_mapping_index = reverse_mapping_index,
			stack_offset = stack_offset,
			module = module,
			**source_update,
		)

	return function


def simple_dynamic_initializer(field_data, name='__init__', stack_offset=0):
	frame = sys._getframe(stack_offset + 1)

	return create_function(name,
		', '.join(('self', *(f'{k}={k}' for k in field_data))),
		'\n'.join(f'self.{k} = {k}' for k in field_data),
		locals = dict_merge_last_priority(frame.f_locals, field_data),
		globals = frame.f_globals,
	)



class simple_base:
	def __init_subclass__(cls):
		cls.__init__ = simple_dynamic_initializer(cls._default_values)

	def __repr__(self):
		to_display = list()
		for key, default in self.__class__._default_values.items():
			if (value := getattr(self, key, default)) != default:
				to_display.append(f'{key}={value!r}')

		inner = ' '.join((self.__class__.__name__, *to_display))
		return f'<{inner}>'



class symbol(simple_base):
	_default_values = dict(
		name = 						None,
	)

	def __repr__(self):
		return f'`{self.name}´'



def iter_type(target):
	seen = set()
	for base in target.mro():
		for key, value in base.__dict__.items():
			if key not in seen:
				seen.add(key)
				yield key, value


MISS = symbol('MISS')

class stack:
	def __init__(self, target, *updates, **named_updates):
		self.target = target
		self.updates = dict()
		for u in updates:
			self.updates.update(u)
		self.updates.update(named_updates)
		self.previous = None

	def __enter__(self):
		assert self.previous is None
		self.previous = tuple(self.target.get(key, MISS) for key in self.updates)
		self.target.update(self.updates)

	def __exit__(self, et, ev, tb):
		for key, value in zip(self.updates, self.previous):
			if value is MISS:
				del self.target[key]
			else:
				self.target[key] = value

