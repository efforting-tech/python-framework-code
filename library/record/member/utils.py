from ..rudimentary import define_record, Abstract_Record
from ...abc import Abstract_Factory
from ... import symbol



class Factory_Interface(Abstract_Factory):
	def __call__(self, descriptor, target):
		setattr(target, descriptor.name, self.function(*self.positional, **self.named))		#TODO -translations, such as the ones in rudimentary (self ref and such)

class Constant_Interface(Abstract_Factory):
	def __call__(self, descriptor, target):
		setattr(target, descriptor.name, self.value)

define_record('factory', positional=('function',), named=dict(positional=symbol.argument.all.positional, named=symbol.argument.all.named), bases=(Abstract_Record, Factory_Interface))
define_record('constant', positional=('value',), bases=(Abstract_Record, Constant_Interface))
