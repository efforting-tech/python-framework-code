

class logging_dict(dict):
	def __getitem__(self, key):
		print('__getitem__', key)
		return super().__getitem__(key)

class logging_type(type):
	def __prepare__(self, bases):
		return logging_dict()


class test(metaclass=logging_type):
	pass


print(1 in test())