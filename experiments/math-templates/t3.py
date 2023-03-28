#Inspired by t2 but here we will put the container types in one place and the rule system in another

from t3_types import *
import itertools
from efforting.mvp4 import abstract_base_classes as abc

[number] = abc.register_abstract_base_classes('number')

abc.register_specific_class('number')(int)
abc.register_specific_class('number')(float)


#print(M.e.numerical_value ** M.e.numerical_value)

class counting_set:
	#TODO - this must use our own hashing function so that for instance -0 and 0 is equal
	def __init__(self, source=None):
		self.count = dict()
		if source:
			self.append_many(source)

	def append_many(self, source):
		for item in source:
			self.append(item)

	def remove_many(self, source):
		for item in source:
			self.remove(item)

	def remove(self, item, value=1):
		if (number := self.count.get(item)) is not None:
			self.count[item] = number - value
		else:
			self.count[item] = -value

	def append(self, item, value=1):
		if (number := self.count.get(item)) is not None:
			self.count[item] = number + value
		else:
			self.count[item] = value

	# def negate(self, item):
	# 	self.append(negate(item), self.count.pop(item))

	def __iter__(self):
		yield from self.count.items()


def resolve_once(e):
	if isinstance(e, pending_operation):
		print('OP', e)
	match e:
		case pending_operation(operation=OP.negate, operands=[operand]):
			return resolve_once(negate(operand))

		case pending_operation(operation=OP.multiply, operands=operands):
			return resolve_once(product(*operands))

		case pending_operation(operation=OP.divide, operands=(dividend, divisor)):
			return resolve_once(product(dividend, reciprocal(divisor)))

		case pending_operation(operation=OP.power, operands=(constant.e, exponent)):
			return function.exp(exponent)

		case pending_operation(operation=OP.product, operands=operands):
			return resolve_once(product(*operands))

		case pending_operation(operation=OP.power, operands=(base, exponent)):
			return resolve_once(power(base, exponent))

		case pending_operation(operation=OP.sum, operands=[operand]):
			return resolve_once(sum(*operand))

		case product(operands=operands):

			cop = counting_set()

			#First we expand any inner products
			for op in map(resolve_once, operands):
				match op:
					case product(operands=sub_operands):
						cop.append_many(sub_operands)

					#case negate(operand=operand):
						#cop.append(operand)
						#cop.negate(operand)

					case power(base=base, exponent=number() as exponent):
						cop.append(base, exponent)

					#case negate(operand=sub_operand):
					#	cop.remove(sub_operand)

					case _:
						#rop.append(op)
						cop.append(op)



			print('---')
			for (a, a_count), (b, b_count) in tuple(itertools.combinations(cop, 2)):

				print('COMB', a, a_count, b, b_count)
				match a, b:
					case negate(operand=sa), negate(operand=sb) if sa is sb:
						print('-sym * -sym', a_count, b_count)
						cop.remove(a, a_count)
						cop.remove(b, b_count)
						cop.append(power(a, a_count + b_count))

					case negate(operand=sa), sb if sa is sb:
						cop.remove(a, a_count)
						cop.remove(b, b_count)
						cop.append(negate(power(a, a_count + b_count)))

					case sa, negate(operand=sb) if sa is sb:
						cop.remove(a, a_count)
						cop.remove(b, b_count)
						cop.append(negate(power(a, a_count + b_count)))

					case power(base=sa, exponent=sa_exp), sb if sa is sb:
						print('POW', sa, sa_exp, sb)

					case sa, power(base=sb, exponent=sb_exp) if sa is sb:
						print('POW', sa, sb, sb_exp)

					case negate(operand=power(base=sa, exponent=sa_exp)), sb if sa is sb:
						print('NEGPOW', sa, sa_exp, sb)

					case sa, negate(operand=power(base=sb, exponent=sb_exp)) if sa is sb:
						print('NEGPOW', sa, sb, sb_exp)


					case power(base=sa, exponent=sa_exp), negate(operand=sb) if sa is sb:
						print('nPOW', sa, sa_exp, sb)

					case negate(operand=sa), power(base=sb, exponent=sb_exp) if sa is sb:
						print('nPOW', sa, sb, sb_exp)

					case negate(operand=power(base=sa, exponent=sa_exp)), negate(operand=sb) if sa is sb:
						print('nNEGPOW', a_count, b_count, sa, sa_exp, sb)
						# a_count * -(X ** sa_exp) * b_count * -X
						cop.remove(a, a_count)
						cop.remove(b, b_count)

						# 5 * -(X ** sa_exp) * 3 * -X
						# -5 * X ** sa_exp * -3 * X
						# 15 * X ** (sa_exp + 1)

						cop.append(power(sa, sa_exp + 1), a_count * b_count)



					case negate(operand=sa), negate(operand=power(base=sb, exponent=sb_exp)) if sa is sb:
						print('nNEGPOW', sa, sb, sb_exp)



					case number(), number():
						print('NUMNUM')
						#cop.remove(a, a_count)
						#cop.remove(b, b_count)
						#raise Exception()
						#cop.append(a * b)

					case number(), product():
						print('numprod')




			rop = list()

			for i, count in tuple(cop):

				match i:
					case number():
						if count == 0:
							pass
						else:
							rop.append(i ** count)

					case negate(operand=number() as n):
						print('NEG', n)

					case _:
						if count == 0:
							pass
						elif count == 1:
							rop.append(i)
						elif count == -1:
							rop.append(negate(i))
						elif count > 1:
							rop.append(power(i, count))
						elif count < -1:
							rop.append(negate(power(i, count)))
						else:
							rop.append(product(i, count))



			return product(*rop)


	return e

def resolve(e):
	for v in range(3):
		e = resolve_once(e)

	return e

#print(resolve(constant.e ** 5))

#print(resolve(constant.pi * constant.tau * constant.tau * constant.pi * constant.tau))
#print(resolve(constant.pi * -constant.pi * -constant.pi * constant.tau * constant.tau / constant.tau))
#print(resolve(constant.pi * constant.pi * constant.pi))

#A = symbol('A')
#B = symbol('B')

#print(resolve(A * A))

#print(M.exp(5))


class symbol_tree_dict(dict):

	def __missing__(self, key):
		new_symbol = pending_symbol_tree(key)
		self[key] = new_symbol
		return new_symbol

	def walk(self):
		for item in self.values():
			yield from item._walk()

class pending_symbol_tree(base):
	_name = RTS.positional()
	_children = RTS.factory(dict)

	def _walk(self):
		yield self
		for child in self._children.values():
			yield from child._walk()

	def __getattr__(self, key):
		assert not key.startswith('_')
		new_symbol = self._children[key] = pending_symbol_tree(f'{self._name}.{key}')
		setattr(self, key, new_symbol)
		return new_symbol

	def __repr__(self):
		return f'{self._name}'

ed = symbol_tree_dict()
v = eval('A ** E1 * A ** E2', {}, ed)

print(resolve(v))