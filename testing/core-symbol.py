SYMBOL_PARENT_LUT = dict()

class Symbol(type):
	def __new__(cls, name, *members):
		scope = dict(
			__name__ = name,
		)

		for m in members:
			scope[m.__name__] = m

		result = super().__new__(cls, name, (), scope)

		for m in members:
			SYMBOL_PARENT_LUT[m] = result

		return result

	def __contains__(self, other):
		ptr = other
		while ptr:
			if ptr is self:
				return True
			ptr = SYMBOL_PARENT_LUT.get(ptr)
		return False


	def __init__(self, *p, **n):
		pass

	def __dir__(self):
		return sorted((m.__name__ for m in self), key=str)

	def __iter__(self):
		yield from (m for m in self.__dict__.values() if isinstance(m, Symbol))

	def __str__(self):
		if parent := SYMBOL_PARENT_LUT.get(self):
			return f'{parent}.{self.__name__}'
		else:
			return self.__name__

	def __repr__(self):
		return f'«S {self}»'

class Local_Symbol(Symbol):
	def __repr__(self):
		return f'«LS {self}»'


class Enum_Choice(Symbol):
	pass

class Enum_Identity(Enum_Choice):
	def __repr__(self):
		return f'«EI {self}»'

class Enum_Value(Enum_Choice):
	def __new__(cls, name, value):
		result = super().__new__(cls, name)
		result.__value = value
		return result

	def __repr__(self):
		return f'«EV {self}: {self.__value!r}»'

	def __int__(self):
		return self.__value

class Enum(Symbol):
	def __new__(cls, name, *members, **values):
		pending_members = list()
		for m in members:
			match m:
				case str():
					pending_members.append(Enum_Identity(m))
				case unsupported:
					raise Exception(unsupported)

		for member_name, value in values.items():
			match value:
				case int():
					pending_members.append(Enum_Value(member_name, value))
				case unsupported:
					raise Exception(unsupported)



		return super().__new__(cls, name, *pending_members)

	def __repr__(self):
		return f'«E {self}»'


# ROOT = Symbol('Symbol',
# 	Symbol('Math',
# 		Symbol('Matrix'),
# 		Symbol('Vector'),
# 		Symbol('Tensor'),
# 	),

# 	Symbol('Aggregator',
# 		Enum('Status',
# 			'Pending',
# 			'Working',
# 			'Finished',
# 			'Aborted',
# 		),
# 	),

# 	Enum('Demo',
# 		Thing = 1,
# 		Stuff = 2,
# 	),
# )

# print()
# print(ROOT)
# print(ROOT.Math)
# print(ROOT.Math.Vector)
# print(ROOT.Aggregator.Status)


# print(dir(ROOT.Math))
# print(tuple(ROOT.Aggregator.Status))

# print(ROOT.Aggregator.Status.Pending in ROOT.Aggregator.Status)
# print(ROOT.Math in ROOT.Aggregator.Status)
# print(ROOT.Math.Matrix in ROOT.Math)
# print(ROOT.Math.Matrix in ROOT)

# print(int(ROOT.Demo.Stuff))
