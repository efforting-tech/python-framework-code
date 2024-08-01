from ..record.base import public
from ..record import member as M
from .. import ABC

@ABC.Data_Condition
class Data_Condition(public.Structure):
	def __and__(self, other):
		assert isinstance(other, ABC.Data_Condition)
		return All(True, self, other)

	def __or__(self, other):
		assert isinstance(other, ABC.Data_Condition)
		return Any(True, self, other)

	def __invert__(self):
		return Not(self)

	def __eq__(self, other):
		return type(self) is type(other) and self.__getstate__() == other.__getstate__()

class Comparative_Data_Condition_Interface:
	value = M.positional()

	def __eq__(self, other):
		return type(self) is type(other) and self.value == other.value


class Sequential_Data_Condition_Interface:
	def __eq__(self, other):
		return type(self) is type(other) and super().__eq__(self, other)

class Sequence_Data_Condition(public.Sequence, Data_Condition):
	pass

class Comparative_Data_Condition(Data_Condition, Comparative_Data_Condition_Interface):
	pass

class All(Sequence_Data_Condition, Comparative_Data_Condition_Interface):
	value = M.named(default=True)

class Any(Sequence_Data_Condition, Comparative_Data_Condition_Interface):
	value = M.named(default=True)

class Not(Data_Condition, Comparative_Data_Condition_Interface):
	pass

class Sequence(Sequence_Data_Condition, Sequential_Data_Condition_Interface):
	pass


class Identity(Comparative_Data_Condition):
	pass

class Equality(Comparative_Data_Condition):
	pass

class Type_Identity(Comparative_Data_Condition):
	pass

class Type_Instance(Comparative_Data_Condition):
	pass

class Type_Subclass(Comparative_Data_Condition):
	pass

class Type_Ancestor(Comparative_Data_Condition):
	pass

class Type_Decendent(Comparative_Data_Condition):
	#Like subclass but without including the top level
	pass

class Structure_Match(Comparative_Data_Condition):
	value = M.all_named()

class Call_And_Compare_Return_Value(Comparative_Data_Condition):
	pass

class Capture(Data_Condition):
	name = M.positional(default=None)

class Capture_Remaining(Data_Condition):
	name = M.positional(default=None)

class Mnemonic(Comparative_Data_Condition):
	pass


@lambda x: x()	#TODO improve
class Always_True(Data_Condition):
	pass

@lambda x: x()	#TODO improve
class Never_True(Data_Condition):
	pass

