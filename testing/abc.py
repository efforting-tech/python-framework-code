class test_abc(Test):
	from efforting.mvp6 import ABC

	class stuff(ABC.Factory):
		pass

	assert(issubclass(stuff, ABC.Factory))