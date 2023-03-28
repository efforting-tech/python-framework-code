#We should distinguis expanding from evaluating

#We need to make a rule system for how the base math symbols interact

from efforting.mvp4 import rudimentary_type_system as RTS
from efforting.mvp4.rudimentary_type_system.bases import public_base

from efforting.mvp4.rudimentary_type_system import representation as REPR

REPR.adjust_field_stack_limit(4)

import itertools


#TODO - convert these to ABC
class expandable:
	pass

class has_type:
	pass

class scalar:
	pass

class composit_expression:
	pass


def evaluate(item):
	if isinstance(item, composit_expression):
		return item.evaluate()
	elif isinstance(item, (symbol, int, float)):
		return item
	else:
		raise Exception(type(item))

def get_type(item):
	if isinstance(item, has_type):
		return item.type
	elif isinstance(item, (tuple, list)):
		return anonymous_vector_instance
	elif isinstance(item, (float, int)):
		return scalar_instance
	elif isinstance(item, symbol):
		return None
	else:
		raise Exception(item)



def expand(item):
	if isinstance(item, expandable):
		return item.expand()
	elif isinstance(item, (tuple, list)):
		result = ()
		for sub_item in item:
			result += expand(sub_item)
		return result
	else:
		return (item,)

class interface:
	class values(expandable):
		def expand(self):
			return self.values

		def __len__(self):
			return len(self.values)


class vector_instance(public_base, interface.values):
	type = RTS.positional()
	values = RTS.positional()

	def get_dict(self):
		return dict(zip(self.type.field_names, self.values))

	def __getattr__(self, key):
		#d = self.get_dict()

		chars = set(key)
		if chars & set(self.type.field_names) == chars:

			return op.swizzle(self, key)

			# if len(key) == 1:
			# 	return d[key]

			# return anonymous_vector_instance(tuple(d[c] for c in key))
		else:
			raise AttributeError(self, key)


class anonymous_vector_instance(public_base, composit_expression, interface.values):
	values = RTS.positional()

	def __repr__(self):
		return repr(self.values)

	def evaluate(self):
		return self.__class__(tuple(map(evaluate, self.values)))

class scalar_instance(public_base, scalar):
	value = RTS.positional()


class vector(public_base):
	name = RTS.positional()
	field_names = RTS.field(None)

	def __len__(self):
		return len(self.field_names)

	def __call__(self, *positional):
		return vector_instance(self, positional)

class op:
	class binary_operation(public_base):
		left = RTS.positional()
		right = RTS.positional()

	class unary_operation(public_base):
		operand = RTS.positional()

	class negate(unary_operation):
		def __repr__(self):
			r = repr(self.operand)
			if ' ' in r:
				r = f'({r})'

			return f'-{r}'

	class nary_operation(public_base):
		operands = RTS.all_positional()

	class dot(binary_operation, composit_expression):
		def evaluate(self):
			le = expand(self.left)
			re = expand(self.right)
			assert len(le) == len(re)
			#We will reuse the left type
			return op.sum(*tuple(l * r for l, r in zip(le, re)))

	class hadamard(binary_operation, composit_expression):

		def evaluate(self):
			le = expand(self.left)
			re = expand(self.right)
			assert len(le) == len(re)

			if len(le) == 1:
				return evaluate(le[0]) * evaluate(re[0])


			#We will reuse the left type
			if not (result_type := get_type(self.left)):
				result_type = anonymous_vector_instance

			return result_type(tuple(l * r for l, r in zip(le, re)))

		def __add__(self, other):
			return op.sum(self, other)

		def __radd__(self, other):
			return op.sum(other, self)

		def __repr__(self):
			l, r = repr(self.left), repr(self.right)
			if ' ' in l:
				l = f'({l})'
			if ' ' in r:
				r = f'({r})'
			return f'{l} * {r}'


	class component(public_base, composit_expression):
		reference = RTS.positional()
		component = RTS.positional()

		def evaluate(self):
			return evaluate(self.reference.get_dict()[self.component])

	class swizzle(public_base, composit_expression, expandable):
		reference = RTS.positional()
		fields = RTS.positional()

		def expand(self):
			return tuple(op.component(self.reference, f) for f in self.fields)


		def __repr__(self):
			r = repr(self.reference)
			if ' ' in r:
				r = f'({r})'

			return f'{r}.{self.fields}'


	class sum(nary_operation, composit_expression):
		def evaluate(self):
			result = evaluate(self.operands[0])
			for o in self.operands[1:]:
				result += evaluate(o)
			return result

		def __add__(self, other):
			return op.sum(*self.operands, other)


class symbol(public_base):
	name = RTS.positional()

	def __mul__(self, other):
		return op.hadamard(self, other)

	def __rmul__(self, other):
		return op.hadamard(other, self)

	def __add__(self, other):
		return op.sum(self, other)

	def __radd__(self, other):
		return op.sum(other, self)

	def __sub__(self, other):
		return op.sum(self, -other)

	def __rsub__(self, other):
		return op.sum(other, -self)

	def __neg__(self):
		return op.negate(self)

	def __repr__(self):
		return self.name


vec2_uv = vector('vec2', 'uv')
vec3 = vector('vec3', 'xyz')


A, B, C, D, E, F, G, H = (symbol(s) for s in 'ABCDEFGH')


X = op.hadamard((vec2_uv(A, B), vec3(C, D, E)), vec3(F, G, H).xyzzy)

for v in range(3):
	print(X)
	print()
	X = evaluate(X)

print('---')

X = op.dot(vec3(10, 20, A), vec3(20, 100, 200))

for v in range(3):
	print(X)
	print()
	X = evaluate(X)

print( A + B)
print( A - B + C - D)