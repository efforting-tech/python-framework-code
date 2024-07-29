from ..record.base import public
from ..record import member as M

class Data_Condition(public.Structure):
	def __and__(self, other):
		assert isinstance(other, Data_Condition)	#TODO - use ABC
		return All(True, self, other)

	def __or__(self, other):
		assert isinstance(other, Data_Condition)	#TODO - use ABC
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


