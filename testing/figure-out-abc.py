#TODO - we should not ugly up the modules like in symbol and abc - it gets messy

from efforting.mvp6 import symbol, ABC
from efforting.mvp6.abc_factory import ABC_LUT


print(ABC.Factory)
print(ABC.Record.Data_Descriptor)

@ABC.Record.Data_Descriptor
@ABC.Text.Line
class my_cls:
	pass

print(ABC_LUT[my_cls])

assert issubclass(my_cls, ABC.Text)

assert issubclass(my_cls, ABC.Record)
assert not issubclass(my_cls, ABC.Factory)

assert isinstance(my_cls(), ABC.Record)
assert not isinstance(my_cls(), ABC.Factory)

assert isinstance(my_cls(), my_cls)

assert isinstance(my_cls(), (ABC.Factory, ABC.Record))
assert isinstance(my_cls(), ABC)



exit()


#Maybe we should just use a decorator for registering instead of adding it as bases
#We should at least document the struggle so we don't do this again and know why we do it a certain way

from efforting.mvp6 import ABC

from efforting.mvp6 import abc_factory as AF


#print(isinstance(123, ABC.Factory))

#Yes - this is terribly uggly
class special_module(type(ABC), AF.ABC_Symbol):
	pass

ABC.__class__ = special_module



print(ABC)

print(ABC.Record in ABC)

print(issubclass(ABC.Record.Member, ABC.Record))
print(issubclass(ABC.Record, ABC))

print(issubclass(ABC.Record.Member, ABC.Factory))
print(issubclass(ABC.Record, ABC.Factory))








exit()
#Otherwise we'd have to mess with both __getattribute__ and __dir__

#Maybe the ABC tree should be a symbol tree but with an __init_subclass__ that takes care of things for us


register = set()
register_ready = False


class ABC_meta(type):
	def __getattribute__(self, key):
		if register_ready and self not in register:
			raise AttributeError()
		return super().__getattribute__(key)


class ABC_base(metaclass=ABC_meta):
	pass

class ABC_Root(ABC_base):
	class stuff(ABC_base):
		class things(ABC_base):
			pass

register |= {ABC_Root, ABC_Root.stuff, ABC_Root.stuff.things}


class concrete(ABC_Root.stuff):
	pass

print('----')

print(dir(concrete))

print('"""')


print(concrete.things)


register_ready = True

print(concrete.things)	#Attribute error

