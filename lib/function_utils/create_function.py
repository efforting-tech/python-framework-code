import textwrap, sys, ast, linecache, time
from threading import Lock

#TODO symbol
MISS = object()


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



#  ___         _         _   _
# |_ _|_ _  __| |___ _ _| |_(_)___ _ _
#  | || ' \/ _` / -_) ' \  _| / _ \ ' \
# |___|_||_\__,_\___|_||_\__|_\___/_||_|

def indent(text, prefix='\t'):
	return textwrap.indent(textwrap.dedent(text).strip(), prefix)

#  ___                        _____            _   _
# / __| ___ _  _ _ _ __ ___  |_   _| _ __ _ __| |_(_)_ _  __ _
# \__ \/ _ \ || | '_/ _/ -_)   | || '_/ _` / _| / / | ' \/ _` |
# |___/\___/\_,_|_| \__\___|   |_||_| \__,_\__|_\_\_|_||_\__, |
#                                                        |___/

class source_info:
	def __init__(self, tracker, file_id, filename):
		self.tracker = tracker
		self.file_id = file_id
		self.filename = filename
		self.created = time.time()

	def update(self, **fields):
		for key, value in fields.items():
			if key in self.tracker.do_not_track:
				continue
			setattr(self, key, value)

		if self.tracker.update_linecache and self.source_code:
			linecache.cache[self.file_id] = (len(self.source_code), None, self.source_code.split('\n'), self.filename)

class source_tracker:
	pattern = '<tracked-{id}>'
	do_not_track = ('constants', 'globals', 'locals', 'reverse_mapping_index', 'stack_offset')
	update_linecache = True

	def __init__(self, registry=None, pattern=None, do_not_track=None, do_track=None, update_linecache=None):

		if registry is not None:
			self.registry = registry
		else:
			self.registry = dict()

		if update_linecache is not None:
			self.update_linecache = update_linecache

		if pattern:
			self.pattern = pattern

		self.do_not_track = set(self.do_not_track)
		if do_not_track:
			self.do_not_track |= set(do_not_track)

		if do_track:
			self.do_not_track -= set(do_track)

		self.lock = Lock()

	def register_new_file(self, filename):
		with self.lock:
			pending_id = len(self.registry)
			index = self.pattern.format(id = pending_id)
			result = self.registry[index] = source_info(self, index, filename)
			return result

#    _   ___ _____   __  __           _           _      _   _
#   /_\ / __|_   _| |  \/  |__ _ _ _ (_)_ __ _  _| |__ _| |_(_)___ _ _
#  / _ \\__ \ | |   | |\/| / _` | ' \| | '_ \ || | / _` |  _| / _ \ ' \
# /_/ \_\___/ |_|   |_|  |_\__,_|_||_|_| .__/\_,_|_\__,_|\__|_\___/_||_|
#                                      |_|

def ast_replace_constants_and_return_mapping(ast_tree, constants):
	mapping_index = dict()

	for constant_name, value in constants.items():
		mapping_index[f'v:{constant_name}'] = value

	class transform_names(ast.NodeTransformer):
		def visit_Name(transformer, node):
			key = f'v:{node.id}'
			if (index := mapping_index.get(key)) is not None:
				return ast.Constant(key)
			else:
				return node

		def visit_Constant(transformer, node):
			if isinstance(node.value, str):
				key = f's:{node.value}'
				mapping_index[key] = node.value
				return ast.Constant(key)
			else:
				return node

	processed_tree = transform_names().visit(ast_tree)
	final_tree = ast.fix_missing_locations(processed_tree)

	return final_tree, mapping_index

#  ___             _   _            __  __           _           _      _   _
# | __|  _ _ _  __| |_(_)___ _ _   |  \/  |__ _ _ _ (_)_ __ _  _| |__ _| |_(_)___ _ _
# | _| || | ' \/ _|  _| / _ \ ' \  | |\/| / _` | ' \| | '_ \ || | / _` |  _| / _ \ ' \
# |_| \_,_|_||_\__|\__|_\___/_||_| |_|  |_\__,_|_||_|_| .__/\_,_|_\__,_|\__|_\___/_||_|
#                                                     |_|

def function_replace_string_constants_using_lut(function, lut):
	def translate_constant(const):
		if isinstance(const, str):
			return lut[const]
		else:
			return const

	function.__code__ = function.__code__.replace(co_consts = tuple(translate_constant(value) for value in function.__code__.co_consts))

#  __  __      _        ___         _
# |  \/  |__ _(_)_ _   | __|__ __ _| |_ _  _ _ _ ___
# | |\/| / _` | | ' \  | _/ -_) _` |  _| || | '_/ -_)
# |_|  |_\__,_|_|_||_| |_|\___\__,_|\__|\_,_|_| \___|

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



#  ___     _                   _   _ _ _ _   _
# | __|_ _| |_ _ _ __ _   _  _| |_(_) (_) |_(_)___ ___
# | _|\ \ /  _| '_/ _` | | || |  _| | | |  _| / -_|_-<
# |___/_\_\\__|_| \__,_|  \_,_|\__|_|_|_|\__|_\___/__/

#TODO - move these

def strict_optional_dict_merge(*source_list):
	result = dict()
	for source in source_list:
		if source:
			for key, value in source.items():
				assert key not in result
				result[key] = value
	return result

def strict_dict_merge(*source_list):
	result = dict()
	for source in source_list:
		for key, value in source.items():
			assert key not in result
			result[key] = value
	return result


def dict_merge_last_priority(*source_list):
	result = dict()
	for source in source_list:
		result.update(source)
	return result

def dict_merge_first_priority(*source_list):
	result = dict()
	for source in reversed(source_list):
		result.update(source)
	return result




def simple_dynamic_initializer(field_data, name='__init__', stack_offset=0):
	frame = sys._getframe(stack_offset + 1)

	return create_function(name,
		', '.join(('self', *(f'{k}={k}' for k in field_data))),
		'\n'.join(f'self.{k} = {k}' for k in field_data),
		locals = dict_merge_last_priority(frame.f_locals, field_data),
		globals = frame.f_globals,
	)

