from efforting.mvp4 import abstract_base_classes as abc


thing = abc.register_condition('some.thing', lambda x: x > 100)



print(isinstance(1, thing))
print(isinstance(1000, thing))

match 10:
	case thing():
		print('10 is thing')

match 1000:
	case thing():
		print('1000 is thing')