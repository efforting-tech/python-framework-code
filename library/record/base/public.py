from ... import symbol
from ..member import Abstract_Member, utils as MU
from .. import member as M
from ..rudimentary import Abstract_Record, Data_Descriptor

#The idea here is to make use of the many ideas for various record definition systems from prior experiments
#But for now the rudimentary system is probably powerful enough that we can have this system here just as a convenient way of defining classes

#TODO - move
def iter_object_using_type(target_object, target_type, default=symbol.miss):
	for key in target_type.__dict__:	#NOTE - we can't use dir because it will sort things
		yield key, getattr(target_object, key, default)

def iter_type(target, default=symbol.miss):
	for cls in reversed(target.mro()):
		yield from iter_object_using_type(target, cls, default)


class Structure(Abstract_Record):
	def __init_subclass__(cls):
		all_names = list()
		for key, value in iter_type(cls, True):
			if isinstance(value, Abstract_Member):
				all_names.append(key)

				#TODO - properly reflect these kinds
				#if isinstance(value, M.positional):
					#kind = symbol.argument.positional_or_named
				#elif isinstance(value, M.named):
					#kind = symbol.argument.positional_or_named

				#TODO convert to match?
				if isinstance(value, M.all_positional):
					setattr(cls, key, Data_Descriptor(key, kind=symbol.argument.all.positional))

				elif isinstance(value, M.all_named):
					setattr(cls, key, Data_Descriptor(key, kind=symbol.argument.all.named))

				elif value.factory and not value.default:
					setattr(cls, key, Data_Descriptor(key, init=MU.factory(value.factory)))

				elif value.default and not value.factory:
					setattr(cls, key, Data_Descriptor(key, init=MU.constant(value.default)))

				elif not value.default and not value.factory:
					setattr(cls, key, Data_Descriptor(key))
				else:
					raise Exception()	#TODO - proper exception

		cls.__match_args__ = tuple(all_names)