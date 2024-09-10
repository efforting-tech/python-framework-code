import sys
from collections import defaultdict

from .factory_helpers import Register_Interface
from .symbol_factory import Symbol

ABC_LUT = defaultdict(set)


def create_ABC_Symbol(name, parent=None, auto_graft=None):
	return ABC_Symbol(name, (), dict(
		parent = parent,
		auto_graft = auto_graft,
	))



#from collections import Counter
#ugly_stats = Counter()

class ABC_Symbol(Symbol, type):
	def __instancecheck__(self, instance):

		# import sys
		# f = sys._getframe(1)
		# while f:
		# 	ugly_stats[repr(f)] += 1
		# 	f = f.f_back


		return self.__subclasscheck__(type(instance))

	def __subclasscheck__(self, klass):

		if klass is not type:
			for cls_to_check in reversed(klass.mro()):
				for item in ABC_LUT[cls_to_check]:
					if item is self or item in self:
						return True

		return klass in self	#This is for checking ABC in ABC

	def __call__(self, target):
		ABC_LUT[target].add(self)
		return target


interface = Register_Interface(create_ABC_Symbol)
register_abc_here = interface.register_entries_here
register_abc_at_target = interface.register_entries_at_target
register_abc = interface.register_entry