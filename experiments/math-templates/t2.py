from efforting.mvp4 import rudimentary_type_system as RTS
from efforting.mvp4.rudimentary_type_system.bases import public_base
from efforting.mvp4.rudimentary_type_system import representation as REPR
from efforting.mvp4.symbols import register_symbol

REPR.adjust_field_stack_limit(4)

FEAT_INIT = False	#Feature for trying to process things as they are created (maybe this should however be part of the rule system)


class OP:
	op = register_symbol('math.operation')
	add = op()
	subtract = op()
	sum = op()
	negate = op()
	multiply = op()
	power = op()

def mwrap(item):
	result = repr(item)
	if ' ' in result:
		return f'({result})'
	else:
		return result

def resolve_operation(operation, *operands):

	if operation is OP.sum:
		return sum(operands)

	if operation is OP.add:
		return sum(operands)

	if operation is OP.subtract:
		return sum((operands[0], *(-o for o in operands[1:])))

	if operation is OP.multiply:
		return product(operands)

	if operation is OP.power:
		return power(*operands)

	if operation is OP.negate:
		return negate(*operands)

	return unresolved_operation(operation, operands)


class math_base_object(public_base):
	def __add__(self, other):
		return resolve_operation(OP.add, self, other)

	def __radd__(self, other):
		return resolve_operation(OP.add, other, self)

	def __sub__(self, other):
		return resolve_operation(OP.subtract, self, other)

	def __rsub__(self, other):
		return resolve_operation(OP.subtract, other, self)

	def __mul__(self, other):
		return resolve_operation(OP.multiply, self, other)

	def __rmul__(self, other):
		return resolve_operation(OP.multiply, other, self)

	def __pow__(self, other):
		return resolve_operation(OP.power, self, other)

	def __rpow__(self, other):
		return resolve_operation(OP.power, other, self)

	def __neg__(self):
		return resolve_operation(OP.negate, self)

class negate(math_base_object):
	operand = RTS.positional()

	def __repr__(self):
		return f'-{mwrap(self.operand)}'

class sum(math_base_object):
	operands = RTS.positional()

	if FEAT_INIT:
		@RTS.initializer
		def init(self):
			resulting_operands = tuple()
			for op in self.operands:
				if isinstance(op, sum):
					resulting_operands += op.operands
				else:
					resulting_operands += (op,)

			self.operands = resulting_operands

	def __repr__(self):
		inner = ', '.join(mwrap(o) for o in self.operands)
		return f'sum({inner})'


class power(math_base_object):
	base = RTS.positional()
	exponent = RTS.positional()

	def __repr__(self):
		return f'{mwrap(self.base)} ** {mwrap(self.exponent)}'


class product(math_base_object):
	operands = RTS.positional()

	if FEAT_INIT:
		@RTS.initializer
		def init(self):
			resulting_operands = tuple()
			for op in self.operands:
				if isinstance(op, product):
					resulting_operands += op.operands
				else:
					resulting_operands += (op,)

			self.operands = resulting_operands

	def __repr__(self):
		inner = ', '.join(mwrap(o) for o in self.operands)
		return f'product({inner})'



class unresolved_operation(math_base_object):
	operation = RTS.positional()
	operands = RTS.positional()

class symbol(math_base_object):
	name = RTS.positional()

	def __repr__(self):
		return self.name

def lerp(begin, end, fraction):
	return (end - begin) * fraction + begin

A = symbol('A')
B = symbol('B')
C = symbol('C')

print(10 + A + 20 - B - 30)

print(lerp(A, B, C))

print(A ** B ** C)