from efforting.mvp4.presets.text_processing import *
import inspect
UNDEFINED = object()


class bound_configurable_function(public_base):
	owner = RTS.positional()
	instance = RTS.positional()
	target = RTS.positional()

	@property
	def __name__(self):
		return self.target.__name__

	#TODO - cache based on instance and target?
	@property
	def __signature__(self):
		r = inspect.signature(self.target)
		new_parameters = dict(r.parameters)
		new_parameters.pop('config')

		for field in self.owner.__dict__.values():
			if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
				if self.instance:
					new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=getattr(self.instance, field.name))
				else:
					new_parameters[field.name] = inspect.Parameter(field.name, inspect.Parameter.KEYWORD_ONLY, default=field.default)

		return inspect.Signature(new_parameters.values())

	def __call__(self, *positional, **named):
		assert self.instance
		config = dict()
		for field in self.owner.__dict__.values():
			if isinstance(field, RTS.field) and field.field_type == RTS.SETTING:
				if (value := named.pop(field.name, UNDEFINED)) is not UNDEFINED:
					config[field.name] = value

		return self.target(self.instance, *positional, config=config, **named)

	def __get__(self, instance, owner):	#Never called but required
			# https://github.com/python/cpython/blob/3adb23a17d25e36bd80874e860835182d851623f/Lib/inspect.py#L320
		raise Exception('This method is only a facade')



class configurable_function(public_base):
	target = RTS.positional()

	def __get__(self, instance, owner):
		return bound_configurable_function(owner, instance, self.target)


class some_fancy_class(public_base):

	cat_count = RTS.setting(3)
	dog_count = RTS.setting(3)

	@configurable_function
	def some_function(self, item, *, stuff='thing', config):
		print(f'Operating on {item!r} and stuff {stuff!r}, using {config}')


s = some_fancy_class()

#s.some_function('target', cat_count=123)
s.cat_count = 5
#print(s.some_function.__signature__)
#print(some_fancy_class.some_function.__signature__)


print(inspect.isroutine(s.some_function))
print(inspect.ismethod(s.some_function))
print(inspect.isclass(s.some_function))
print(inspect.isfunction(s.some_function))
print(inspect.ismethoddescriptor(s.some_function))	#

#NOTE One drawback with this current implementation is that if we are checking s.some_function we actually get s.__class__.some_function which is unfortunate but not a deal breaker.

#print(type(s.some_function).__get__)

#help(some_fancy_class.some_function)
#help(s.some_function)
#help(s)
print(s.some_function('it'))

#print(inspect.signature(s.some_function))falt