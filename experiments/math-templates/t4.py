#Inspired by t2 but here we will put the container types in one place and the rule system in another

from t3_types import *
import itertools



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


def resolve_pending(e):

	op_lut = {
		OP.add: 		add,
		OP.subtract: 	subtract,
		OP.multiply: 	multiply,
		OP.divide: 		divide,
		OP.power:	 	power,
		OP.negate:		negate,
	}

	match e:
		case pending_operation(operation=op, operands=operands) if (rtype := op_lut.get(op)):
			return rtype(*map(resolve_pending, operands))

		case function_base(operands=operands):
			return e.__class__(*map(resolve_pending, operands))

	return e

# def resolve(e):
# 	for v in range(3):
# 		e = resolve_once(e)

# 	return e

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

	def eval(self, expression):
		return eval(expression.strip(), {}, self)

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

function_lut = {n: f for n, f in function.__dict__.items() if not n.startswith('_')}
constant_lut = {n: c for n, c in constant.__dict__.items() if not n.startswith('_')}


ed = symbol_tree_dict(function_lut, **constant_lut, matrix=matrix)
#v = eval('A ** E1 * A ** E2', {}, ed)
#v = eval('A ** (E1 * E2)', {}, ed)

v = resolve_pending(ed.eval('x * sin(y * tau) / x'))



M2 = resolve_pending(ed.eval('''
	matrix(
		(					#Z0
			(1, tau),
			(pi, -1),
		),
		(
			(0, sin(X)),	#Z1
			(cos(X), 0),
		),
		dimensional_names = 'xyz',
	)
'''))

# print(M2.dimensions)	#(2, 2, 2)
# print(M2.ordering)
# print(M2)				#((1, τ), (π, -1)), ((0, sin(X)), (cos(X), 0))




M1 = resolve_pending(ed.eval('''
	matrix(
		(1, 2, 3),
		(4, 5, 6),
		(7, 8, 9),

		dimensional_names = ('row', 'col'),
	)

'''))





#s = M1.get_traversal_stride()
#dim = M1.dimensions

#Slicing and serialization needs to be figured out for matrices

#def serialize(depth, offset, item):



# for s_dim, stride in s.items():
# 	print(s_dim, stride)
# 	for index in range(dim[s_dim]):
# 		print(index * stride)


#M1.ordering = ('col', 'row')

for c in M1.serialize():
	print(c)

print(M1)
M1.ordering = 'col', 'row'
M1.apply_serial_data((10, 20, 30, 40, 50, 60, 70, 80, 90))
print(M1)

print(M1.ascii_format())


	# for index, sub_item in enumerate(item):
	# 	sub_offset = offset + s[depth] * index
	# 	if isinstance(sub_item, (tuple, list)): 	#TODO - abc
	# 		serialize(depth + 1, sub_offset, sub_item)
	# 	else:
	# 		print(sub_offset, sub_item)


#serialize(0, 0, M1.sub_elements)

# for d in range(M1.dimensionality):
# 	print(d, s[d], dim[d])

# 	for p in range(dim[d]):
# 		print(p)



