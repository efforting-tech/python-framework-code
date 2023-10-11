import types, sys

#decorator
class lazy_init:
	def __init__(self, initialization_script):
		self.initialization_script = initialization_script

	def __call__(self, function):
		f = sys._getframe(1)
		return decorated_lazy_init(function, self, f.f_globals, f.f_locals)

class decorated_lazy_init():
	def __init__(self, target_function, initializer, f_globals, f_locals):
		self._target_function_ = target_function
		self._initializer_ = initializer
		self._f_globals_ = f_globals
		self._f_locals_ = f_locals

		#Introspection/help
		self.__name__ = target_function.__name__
		self.__doc__ = target_function.__doc__

	#Introspection/help
	@property
	def __signature__(self):
		import inspect
		return inspect.signature(self._target_function_)

	#Introspection/help
	def __get__(self, instance, owner):	#Never called but required
			# https://github.com/python/cpython/blob/3adb23a17d25e36bd80874e860835182d851623f/Lib/inspect.py#L320
			# Note that we also need __name__ and __signature__ for this to work the way we want.
		raise Exception('This method is only a facade')

	def __call__(self, *positionals, **named):
		import textwrap, inspect, ast

		initscript = textwrap.dedent(self._initializer_.initialization_script)
		ast_func = ast.parse(inspect.getsource(self._target_function_)).body[0]
		assert len(ast_func.decorator_list) == 1	#We currently only support being the sole decorator
		ast_func.decorator_list.clear()	#Strip decorator
		fdef = ast.unparse(ast_func)	#Get function definition

		python_code = f'{initscript}\n{fdef}'	#Prepare local init script and function redefinition

		#In this version we will clobber f_locals (which will be module dict in most common case)
		exec(python_code, self._f_globals_, self._f_locals_)
		func = self._f_locals_[self._target_function_.__name__]

		#Call function
		return func(*positionals, **named)
