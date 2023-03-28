#The testing library should be completely decoupled from the parent library and shall be based on /home/devilholk/Projects/test-framework-python ( github.com:efforting-tech/python-test-framework.git )

from .type_system import simple_base, symbol, iter_type, stack
from . import state
import builtins, time, sys

SHOULD_NOT_FAIL = symbol('SHOULD_NOT_FAIL')
FAILURE = symbol('FAILURE')
SUCCESS = symbol('SUCCESS')


basic_test = dict(
	name =						None,
	description =				None,
	index = 					None,
	skip =						False,
	title = 					None,

	parent = 					None,
	sub_tests = 				None,

)

class test(simple_base):
	_default_values = dict(
		**basic_test,
		test_function = 			None,
		local_frame = 				None,
		exception_condition = 		SHOULD_NOT_FAIL,
	)

	def run(self):
		result = test_result(self)
		result.log_started()

		with stack(self.local_frame.f_globals, __TEST__=self):
			try:
				exec(self.test_function.__code__, self.local_frame.f_globals, self.local_frame.f_locals)
			except BaseException as e:

				if self.exception_condition is SHOULD_NOT_FAIL:
					result.log_exception(e)
					result.result = FAILURE
				else:
					raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
			else:
				if self.exception_condition is SHOULD_NOT_FAIL:
					result.result = SUCCESS
				else:
					raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature


		result.log_finished()

		return result

class test_group(simple_base):
	_default_values = dict(
		**basic_test,
	)

	def run(self):
		result = test_group_result(self)
		result.log_started()
		for child in self.sub_tests:
			result.append_sub_result(child.run())

		result.log_finished()
		return result



basic_result = dict(
	test = 						None,
	started_walltime =			None,
	started = 					None,
	finished = 					None,
	result = 					None,
)

class common_test_result_interface:
	def log_started(self):
		assert self.started_walltime is None and self.started is None
		self.started_walltime = time.time()
		self.started = time.monotonic()

	def log_finished(self):	#non-idempotent
		assert self.finished is None
		self.finished = time.monotonic()

	@property
	def duration(self):
		return self.finished - self.started

class test_result(simple_base, common_test_result_interface):
	_default_values = dict(
		**basic_result,
		exception =					None,
	)

	def log_exception(self, exception):
		self.exception = exception

	def present(self, indent=''):
		print(f'{indent}{self.test.title or self.test.name} - {self.result} ({self.exception!r})')

class test_group_result(simple_base, common_test_result_interface):
	_default_values = dict(
		**basic_result,
		sub_results =				None,
	)

	def present(self, indent=''):
		if self.sub_results:
			print(f'{indent}{self.test.name}')
			for sr in self.sub_results:
				sr.present(f'{indent}  ')

	def append_sub_result(self, sub_result):
		if not self.sub_results:
			self.sub_results = [sub_result]
		else:
			self.sub_results.append(sub_result)



def resolve_test_or_test_group(item):
	#TODO - support lookup by name?
	match item:
		case test() | test_group():
			return item

	raise TypeError(item)

def resolve_possible_list_of_tests_or_groups(item):
	match item:
		case None:
			return ()
		case tuple():
			return tuple(resolve_test_or_test_group(t) for t in item)

	raise TypeError(item)

def create_fqn(name, index):
	match index:
		case None:
			return name
		case str() | int():
			return f'{name}/{index}'

	raise TypeError(name, index)

def register_test(name, index, test_function, local_frame):
	fqn = create_fqn(name, index)
	result = test(fqn, index=index, local_frame=local_frame, test_function=test_function)

	if state.test_stack:
		parent = state.test_stack[-1]
		test.parent = parent
		parent.sub_tests += (result,)

	assert fqn not in state.directory
	state.directory[fqn] = result
	return result


def register_test_group(name, index=None, include=None):
	fqn = create_fqn(name, index)
	result = test_group(fqn, sub_tests=resolve_possible_list_of_tests_or_groups(include), index=index)
	assert fqn not in state.directory
	state.directory[fqn] = result
	return result

class basic_features:

	@staticmethod
	def __build_class__(func, name, *bases, metaclass=type, **kwds):
		full_name = '.'.join((*(f.__name__ for f in state.class_stack), name))
		index = kwds.pop('index', None)
		if Test in bases:
			return register_test(full_name, index, func, sys._getframe(1), **kwds)
		elif TestGroup in bases:
			result = register_test_group(full_name, index, **kwds)
			state.class_stack.append(func)
			state.test_stack.append(result)
			resulting_class = state.original_builtins['__build_class__'](func, name, metaclass=metaclass)
			result.description = resulting_class.__doc__
			assert state.test_stack.pop() is result
			assert state.class_stack.pop() is func
			return result

		else:
			state.class_stack.append(func)
			result = state.original_builtins['__build_class__'](func, name, *bases, metaclass=metaclass, **kwds)
			assert state.class_stack.pop() is func
			return result


	class Test:
		pass

	class TestGroup:
		pass

class standard_features(basic_features):
	#TODO - create examples for use (check examples/demo1.py from upstream)
	@staticmethod
	def IterVars(name_list):
		calling_frame = sys._getframe(1)

		for name in name_list:
			yield name, calling_frame.f_locals[name]


	@staticmethod
	def GlobVars(glob, sort=True):
		calling_frame = sys._getframe(1)
		vars = (k for k in tuple(calling_frame.f_locals.keys()) if fnmatch.fnmatch(k, glob))

		if sort:
			vars = sorted(vars)

		for k in vars:
			yield k, calling_frame.f_locals[k]

	@staticmethod
	def DerivedTypes(base_type, information_source='locals'):
		#Note - when information_source is locals, (key, ref) tuples are yielded, but if information_source is gc, only ref is yielded
		if information_source == 'locals':
			calling_frame = sys._getframe(1)
			for k, v in tuple(calling_frame.f_locals.items()):
				if isinstance(v, type) and v is not base_type and issubclass(v, base_type):
					yield k, v
		elif information_source == 'gc':
			import gc

			meta_type = type(base_type)
			for item in gc.get_objects():
				if isinstance(item, meta_type) and issubclass(item, base_type) and item is not base_type:
					yield item

		else:
			raise Exception('No such information source: {information_source!r}')





def load_testing_framework(feature_set=standard_features):
	if state.original_builtins is not None:
		return

	state.original_builtins = dict(builtins.__dict__)

	for k, v in iter_type(feature_set):
		if isinstance(v, (type, staticmethod)):
			builtins.__dict__[k] = v


def unload_testing_framework():
	raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature


