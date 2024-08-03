from ..rudimentary import define_record, Abstract_Record
from ... import ABC
from ... import symbol


@ABC.Factory
class Factory_Interface:
	def __call__(self, descriptor, target):
		value = self.function(*self.positional, **self.named)

		if value is symbol.target.instance:
			value = target

		setattr(target, descriptor.name, value)

@ABC.Factory
class Constant_Interface:
	def __call__(self, descriptor, target):

		if (value := self.value) is symbol.target.instance:
			value = target

		setattr(target, descriptor.name, value)

define_record('factory', positional=('function',), named=dict(positional=symbol.argument.all.positional, named=symbol.argument.all.named), bases=(Abstract_Record, Factory_Interface))
define_record('constant', positional=('value',), bases=(Abstract_Record, Constant_Interface))
