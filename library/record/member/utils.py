from ..rudimentary import define_record, Abstract_Record
from ... import ABC
from ... import Symbol


@ABC.Factory
class Factory_Interface:
	def __call__(self, descriptor, target):
		#TODO - we should be able to have symbol.target.instance in arguments as well
		value = self.function(*self.positional, **self.named)

		if value is Symbol.Target.Instance:
			value = target

		setattr(target, descriptor.name, value)

@ABC.Factory
class Constant_Interface:
	def __call__(self, descriptor, target):

		if (value := self.value) is Symbol.Target.Instance:
			value = target

		setattr(target, descriptor.name, value)

define_record('factory', positional=('function',), named=dict(positional=Symbol.Argument.All.Positional, named=Symbol.Argument.All.Named), bases=(Abstract_Record, Factory_Interface))
define_record('constant', positional=('value',), bases=(Abstract_Record, Constant_Interface))
