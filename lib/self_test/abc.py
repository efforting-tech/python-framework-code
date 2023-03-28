from efforting.mvp4.testing import load_testing_framework, unload_testing_framework
load_testing_framework()


from efforting.mvp4 import abstract_base_classes as abc

class directory(TestGroup):
	'Testing various aspects of the directory'

	class register_abc(Test):	#TODO divvy up in sub tests
		'Registering an abstract base class'

		A, B = abc.register_abstract_base_classes(*'hello world'.split())

		assert A.__name__ == 'hello'
		assert B.__name__ == 'world'

		assert abc.ABC_DIRECTORY[A].symbol is A
		assert abc.ABC_DIRECTORY[B].symbol is B

		abc.discard_abstract_base_classes('hello', B)

		assert A not in abc.ABC_DIRECTORY


	class instance_checking(Test):
		'Testing various aspects of instance checking'

		pizza_topping = abc.register_condition('pizza.topping', lambda x: 'pineapple' not in x)
		assert isinstance(['bacon'], pizza_topping)
		assert not isinstance(['pineapple'], pizza_topping)


class all(TestGroup, include=(directory,)):
	pass

all.run().present()