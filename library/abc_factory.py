import sys
from collections import defaultdict

from .factory_helpers import Register_Interface
from .symbol_factory import Symbol

ABC_LUT = defaultdict(set)

class ABC_Symbol(Symbol):
	def __instancecheck__(self, instance):
		return self.__subclasscheck__(type(instance))

	def __subclasscheck__(self, klass):
		for item in ABC_LUT[klass]:
			if item in self:
				return True

		return klass in self	#This is for checking ABC in ABC

	def __call__(self, target):
		ABC_LUT[target].add(self)
		return target


interface = Register_Interface(ABC_Symbol)
register_abc_here = interface.register_entries_here
register_abc_at_target = interface.register_entries_at_target
register_abc = interface.register_entry