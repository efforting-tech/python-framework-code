import inspect, sys, ast, textwrap
from .. import rudimentary_type_system as RTS
from .bases import public_base
#from ..data_utils import config_ro_access
UNDEFINED = object()#TODO symbol
FIRST_AVAILABLE = object()	#TODO symbol
LAST_AVAILABLE = object()
MISS = object()


class config_ro_access:
	def __init__(self, target):
		self._target = dict(target)

	def _resolve(self):
		result = dict()
		for key, value in self._target.items():
			if isinstance(value, weak_and_lazy):
				self._target[key] = result[key] = value.resolve()
			else:
				result[key] = value

		return result

	def __getattr__(self, key):
		try:
			item = self._target[key]
		except KeyError:
			raise AttributeError(f'{self.__class__.__qualname__}({self._target}) does not contain the key {key}')

		if isinstance(item, weak_and_lazy):
			result = self._target[key] = item.resolve()
			return result
		else:
			return item



#WARNING - this all is deprecated for now since /home/devilholk/Projects/code-base-search-tool/experiments/improved-parser-archive.py is a better variant.


# class bound_configurable_function(public_base):
# 	#NOTE - possibly deprecated
# 	owner = RTS.positional()
# 	instance = RTS.positional()
# 	target = RTS.positional()

# 	@property
# 	def __name__(self):
# 		return self.target.__name__

# 	#TODO - cache based on instance and target?
# 	@property
# 	def __signature__(self):
# 		r = inspect.signature(self.target)
# 		new_parameters = dict(r.parameters)
# 		new_parameters.pop('config')

# 		for field in self.owner.__dict__.values():
# 			if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
# 				if self.instance:
# 					new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=getattr(self.instance, field.name))
# 				else:
# 					new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=field.get_or_create_default(self.instance))

# 		return inspect.Signature(new_parameters.values())

# 	def call_with_config(self, config, *positional, **named):
# 		return self.target(self.instance or self.owner, *positional, config=config, **named)

# 	def __call__(self, *positional, **named):
# 		#assert self.instance
# 		config = dict()
# 		for field in self.owner.__dict__.values():
# 			if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
# 				if (value := named.pop(field.name, UNDEFINED)) is not UNDEFINED:
# 					config[field.name] = value
# 				else:
# 					config[field.name] = field.get_or_create_default(self.instance)

# 		return self.target(self.instance or self.owner, *positional, config=config_ro_access(config), **named)


# 	def __get__(self, instance, owner):	#Never called but required
# 			# https://github.com/python/cpython/blob/3adb23a17d25e36bd80874e860835182d851623f/Lib/inspect.py#L320
# 		raise Exception('This method is only a facade')



def get_settings(target):
	result = dict()

	for base in reversed(target.mro()):
		for field in base.__dict__.values():
			if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
				result[field.name] = field

	return result



class configurable_function(public_base):
	target = RTS.positional()
	settings = RTS.positional()

	def __get__(self, instance, owner):
		return bound_configurable_function(owner, instance, self.target)


class classmethod_with_specified_settings(public_base):
	classes = RTS.all_positional(field_type=RTS.SETTING)
	merge_settings = RTS.setting(False)

	@RTS.initializer
	def verify_classes(self):
		for c in self.classes:	#TODO - test against proper ABC
			assert isinstance(c, type) or c is RTS.SELF

	def __call__(self, function):
		#print(self, function)
		#print(self)
		#print(bound_configurable_function())

		#return configurable_function(function)
		return pending_classmethod_configuration(self, function)



class method_with_specified_settings(classmethod_with_specified_settings):
	#todo - both classmethod and method should probably be derived from the same base

	def __call__(self, function):
		return pending_method_configuration(self, function)



class pending_classmethod_configuration(public_base):
	configuration = RTS.positional()
	function = RTS.positional()

	def __get__(self, instance, owner):

		settings = dict()
		target = instance or owner

		for c in self.configuration.classes:
			if c is RTS.SELF:
				c = owner

			for key, field in get_settings(c).items():

				if key in settings:
					#Merge strategy
					match [self.configuration.merge_settings.get(key)]:
						case [FIRST_AVAILABLE] if FIRST_AVAILABLE:
							pass
						case [LAST_AVAILABLE]:
							settings[key] = field
						case [None]:
							raise Exception(f'No merge strategy defined for named setting {key!r}')
						case _ as unhandled:
							raise Exception(f'Unknown merge strategy: {unhandled!r}')
				else:
					settings[key] = field

		return bound_configurable_classmethod(self.configuration, instance, owner, settings, self.function)

class pending_method_configuration(pending_classmethod_configuration):
	#todo - both classmethod and method should probably be derived from the same base
	#todo - should return bound_configurable_method when __get__
	pass

class bound_configurable_classmethod(public_base):
	configuration = RTS.positional()
	instance = RTS.positional()
	owner = RTS.positional()
	settings = RTS.positional()
	function = RTS.positional()
	signature = RTS.state()

	@RTS.initializer
	def prepare_signature(self):
		self.signature = inspect.signature(self.function)

	@property
	def __name__(self):
		target = self.instance or self.owner
		return target.__name__

	def __get__(self, instance, owner):	#Never called but required
			# https://github.com/python/cpython/blob/3adb23a17d25e36bd80874e860835182d851623f/Lib/inspect.py#L320
			# Note that we also need __name__ and __signature__ for this to work the way we want.
		raise Exception('This method is only a facade')

	@property
	def __signature__(self):

		new_parameters = dict(self.signature.parameters)
		settings_name_list = tuple(self.signature.parameters.keys())[-len(self.configuration.classes):]
		target = self.instance or self.owner

		for settings_name in settings_name_list:
			new_parameters.pop(settings_name)

		for settings_class in self.configuration.classes:

			if settings_class is RTS.SELF:
				settings_class = self.owner

			for field in settings_class.__dict__.values():
				if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
					#TODO - can we add docs or annotations?
					if self.instance:
						new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=getattr(self.instance, field.name))
					else:
						new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=field.get_or_create_default(self.instance))

		return inspect.Signature(new_parameters.values())


	# def call_with_config(self, config, *positional, **named):
	# 	settings_name_list = tuple(self.signature.parameters.keys())[-len(self.configuration.classes):]
	# 	print(settings_name_list)

	# 	target = self.instance or self.owner	#Todo - make a property for target? (here we could also care about classmethod/method/static etc)
	# 	return self.function(target, *positional, config=config, **named)

	# def call_with_config_and_updates(self, config, *positional, **updates):

	# 	settings_name_list = tuple(self.signature.parameters.keys())[-len(self.configuration.classes):]
	# 	print(settings_name_list)

	# 	target = self.instance or self.owner	#Todo - make a property for target? (here we could also care about classmethod/method/static etc)
	# 	config._target = dict(config._target, **updates)	#TODO - dict merge?
	# 	return self.function(target, *positional, config=config)


	#TODO - check codebase for calls to here in case we have broken something - write tests!
	def call_with_config(self, *positional, **updates):
		settings_name_list = tuple(self.signature.parameters.keys())[-len(self.configuration.classes):]
		settings = dict()
		unutilized_settings = set(updates)
		target = self.instance or self.owner

		assert len(positional) >= len(settings_name_list)

		for settings_name, c, positional_config_ref in zip(settings_name_list, self.configuration.classes, positional):

			if c is RTS.SELF:
				c = self.owner

			#This is not very pretty - it needs at least documentation and maybe then we can figure out a better way
			cref = settings[settings_name] = config_ro_access(positional_config_ref._target)
			class_settings = cref._target

			for key, field in get_settings(c).items():
				if (settings_value := updates.get(key, MISS)) is not MISS:
					unutilized_settings.discard(key)
					class_settings[key] = settings_value

				elif self.instance and (settings_value := getattr(self.instance, field.name, MISS)) is not MISS:
					existing = class_settings.get(key, MISS)
					if isinstance(existing, weak_and_lazy) or existing is MISS:	#If existing setting is not existing or weak, we override it
						class_settings[key] = settings_value
					else:	#Existing setting exists and is not weak
						class_settings[key] = existing

				else:
					class_settings[key] = weak_and_lazy(field.get_or_create_default, target)


		assert not unutilized_settings, f'The following settings was not mapped to anything: {unutilized_settings}.'


		return self.function(target, *positional[len(settings_name_list):], **settings)





	def __call__(self, *positional, **named):

		settings_name_list = tuple(self.signature.parameters.keys())[-len(self.configuration.classes):]
		settings = dict()
		unutilized_settings = set(named)
		target = self.instance or self.owner

		for settings_name, c in zip(settings_name_list, self.configuration.classes):
			if c is RTS.SELF:
				c = self.owner

			config_object = settings[settings_name] = config_ro_access(dict())
			class_settings = config_object._target

			for key, field in get_settings(c).items():
				if (settings_value := named.get(key, MISS)) is not MISS:
					unutilized_settings.discard(key)
					class_settings[key] = settings_value
				elif self.instance and (settings_value := getattr(self.instance, field.name, MISS)) is not MISS:
					class_settings[key] = settings_value
				else:
					class_settings[key] = weak_and_lazy(field.get_or_create_default, target)


		assert not unutilized_settings, f'The following settings was not mapped to anything: {unutilized_settings}.'
		return self.function(target, *positional, **settings)





class weak_and_lazy(public_base):
	factory = RTS.positional()
	positional = RTS.all_positional()
	named = RTS.all_named()

	def resolve(self):
		return self.factory(*self.positional, **self.named)

#Possibly deprecated
if False:


	def maybe_assign_cls(name, self='cls'):
		return ast.If(ast.Compare(ast.Name(name, ast.Load()), [ast.Is()], [ast.Name('DEFAULT', ast.Load())]), [ast.Assign([ast.Name(name, ast.Store())], ast.Attribute(ast.Attribute(ast.Name(self, ast.Load()), name, ast.Load()), 'default', ast.Load()), None)], [])

	def maybe_assign_self(name, self='self'):
		return ast.If(ast.Compare(ast.Name(name, ast.Load()), [ast.Is()], [ast.Name('DEFAULT', ast.Load())]), [ast.Assign([ast.Name(name, ast.Store())], ast.Attribute(ast.Name(self, ast.Load()), name, ast.Load()), None)], [])

	def membermethod_with_settings(f, stack_offset=0, assignment=maybe_assign_self):
		frame = sys._getframe(1 + stack_offset)
		settings = set()
		for name, value in frame.f_locals.items():
			if isinstance(value, RTS.field):
				if value.field_type is RTS.SETTING:
					settings.add(name)

		signature = inspect.signature(f)

		new_args = list()
		defaults = list()
		module = ast.parse(textwrap.dedent(inspect.getsource(f)))
		function_body = module.body[0].body
		first_arg = None

		first_line_in_new_body = module.body[0].lineno

		for name, parameter in signature.parameters.items():
			if first_arg is None:
				first_arg = name
			if name in settings:
				assert parameter == inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)	#This assertion makes sure the parameter is a regular one
				#new_args.append(f'{name}=DEFAULT')
				new_args.append(ast.arg(name))
				defaults.append(ast.Name('DEFAULT', ast.Load()))
				function_body.insert(0, assignment(name, first_arg))

			else:
				pass
				new_args.append(ast.arg(name))
				#new_args.append(parameter)


		delta_lines = f.__code__.co_firstlineno - first_line_in_new_body + 1
		tree = ast.increment_lineno(ast.fix_missing_locations(ast.Module([ast.FunctionDef(f.__name__, ast.arguments([], new_args, None, [], [], None, defaults), function_body, [])], [])), delta_lines)

		#TODO - harmonize this with create_function
		code = compile(tree, '<function>', 'exec')
		exec(code, frame.f_globals, frame.f_locals)

		func = frame.f_locals[f.__name__]
		return func

	def classmethod_with_settings(f):
		return classmethod(membermethod_with_settings(f, stack_offset=1, assignment=maybe_assign_cls))


	# def classmethod_with_settings(f):

	# 	settings = set()
	# 	for name, value in sys._getframe(1).f_locals.items():
	# 		if isinstance(value, RTS.field):
	# 			if value.field_type is RTS.SETTING:
	# 				settings.add(name)

	# 	signature = inspect.signature(f)

	# 	new_args = list()
	# 	init = list()

	# 	for name, parameter in signature.parameters.items():
	# 		if name in settings:
	# 			assert parameter == inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)	#This assertion makes sure the parameter is a regular one
	# 			new_args.append(f'{name}=DEFAULT')
	# 			init.append(f'if {name} is DEFAULT:')
	# 			init.append(f'	parameter = self.{name}')

	# 		else:
	# 			new_args.append(parameter)



	# 	print(init)
	# 	print(new_args)
	# 	match ast.parse(textwrap.dedent(inspect.getsource(f))):
	# 		case ast.Module(body=[ast.FunctionDef(body=function_body)]):
	# 			print(ast.unparse(function_body))

	# 		case _ as unhandled:
	# 			raise Exception(f'The value {unhandled!r} could not be handled')



	# 	exit()