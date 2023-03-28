from .. import rudimentary_type_system as RTS
from ..rudimentary_type_system.bases import public_base
from ..data_utils import subscope
from ..symbols import register_symbol
from .. import abstract_base_classes as abc

import builtins as B

#Note - these abstract types does not encode that integers are subsets of numbers and so on but focuses on the data type in the more programming sense
#Also note - we may refine this a bit later on to be able to provide things useful both from a programming and math point of view which is the ultimate goal
number, real, integer, scalar, complex, imaginary = abc.register_abstract_base_classes(*'number real integer scalar complex imaginary'.split())	#TODO allow for single string without split


abc.register_specific_class('number')(int)
abc.register_specific_class('number')(float)

#Note - sometimes we will use subconditions to resolve some target when doing type checking, we should probably try to generalize this a bit as this table becomes harder to maintain
abc.register_specific_class('integer')(int)
abc.register_condition('integer', lambda n: isinstance(n, float) and n % 1.0 == 0.0)

abc.register_specific_class('real')(number)
abc.register_condition('real', lambda n: isinstance(n, B.complex) and n.imag == 0)
abc.register_condition('real', lambda n: isinstance(n, constant) and isinstance(n.numerical_value, real))

abc.register_condition('imaginary', lambda n: isinstance(n, B.complex) and n.real == 0)
abc.register_condition('imaginary', lambda n: isinstance(n, constant) and isinstance(n.numerical_value, imaginary))

abc.register_specific_class('scalar')(number)
abc.register_condition('scalar', lambda n: isinstance(n, constant) and isinstance(n.numerical_value, scalar))

abc.register_specific_class('complex')(B.complex)
abc.register_condition('complex', lambda n: isinstance(n, constant) and isinstance(n.numerical_value, complex))



#Should also define symbols here

class OP:
	op = register_symbol('math.operation')

	negate = op()
	invert = op()

	add = op()
	subtract = op()

	multiply = op()
	divide = op()

	power = op()

	equal = op()
	not_equal = op()

	greater_than = op()
	less_than = op()
	greater_than_or_equal = op()
	less_than_or_equal = op()

	belongs_to = op()




class pending_operation_factory(public_base):
	operation = RTS.positional()
	operands = RTS.all_positional()

	def __call__(self, *operands):
		return pending_operation(self.operation, *self.operands, *operands)

	def __get__(self, instance, owner):
		if owner is None:
			return self

		return self.__class__(self.operation, *self.operands, instance)


class base(public_base):
	#TODO - this should be marked as abstract and define or refer to an API def
	with subscope() as ss:
		bin_ops = dict(
			add = 		OP.add,
			sub = 		OP.subtract,
			mul = 		OP.multiply,
			truediv = 	OP.divide,
			pow = 		OP.power,
			eq = 		OP.equal,
			ne = 		OP.not_equal,
		)

		for name, op in bin_ops.items():
			ss.export(f'__{name}__', pending_operation_factory(op))
			ss.export(f'__r{name}__', pending_operation_factory(op))

	__neg__ = pending_operation_factory(OP.negate)



class operation(base):
	pass

class unary_operation(operation):
	pass

# class binary_operation(operation):
# 	pass

class nary_operation(operation):
	operands = RTS.all_positional()

class primitive_token(public_base):
	pass

class function(base):
	operands = RTS.all_positional()
	format = '{format_container(*_.operands)}'



class pending_operation(base):
	operation = RTS.positional()
	operands = RTS.all_positional()
	format = '{format_container(_.operation, *_.operands)}'



#  ___     _       _ _   _           _____    _
# | _ \_ _(_)_ __ (_) |_(_)_ _____  |_   _|__| |_____ _ _  ___
# |  _/ '_| | '  \| |  _| \ V / -_)   | |/ _ \ / / -_) ' \(_-<
# |_| |_| |_|_|_|_|_|\__|_|\_/\___|   |_|\___/_\_\___|_||_/__/

class symbol(primitive_token):
	name = RTS.positional()
	format = RTS.field('{name}')




class constant(primitive_token, base):
	name = RTS.positional()
	numerical_value = RTS.positional()
	format = '{name}'



UNDEFINED = symbol('UNDEFINED', '≟')	#Maybe find a better symbol
