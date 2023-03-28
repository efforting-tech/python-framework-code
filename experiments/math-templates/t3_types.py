from efforting.mvp4 import rudimentary_type_system as RTS
from efforting.mvp4.rudimentary_type_system.bases import public_base
from efforting.mvp4.rudimentary_type_system.representation import local_fields as represent_local_fields
from efforting.mvp4.rudimentary_type_system.introspection import get_fields
#from efforting.mvp4.rudimentary_type_system import representation as REPR
from efforting.mvp4.symbols import register_symbol
from efforting.mvp4 import abstract_base_classes as abc
from collections.abc import Mapping

import math, types


[number] = abc.register_abstract_base_classes('number')
abc.register_specific_class('number')(int)
abc.register_specific_class('number')(float)

#Note - these abstract types does not encode that integers are subsets of numbers and so on but focuses on the data type in the more programming sense
[integer] = abc.register_abstract_base_classes('integer')
abc.register_specific_class('integer')(int)
abc.register_conditional_class('integer', lambda n: isinstance(n, float) and n % 1.0 == 0.0)



#Note - we want to use a function to resolve objects so that for instance, if we need a vector for something and that something is given as a tuple where one of the elements needs expansion, we want a cetralized resolution for this


from t4_formatting import ascii_format_vector



def ensure_mutable_sequence(item):
	#TODO - use more rule sets and ABC - we may also employ some generic API for some mutable_sequence ABC
	if isinstance(item, (tuple, list)):
		return [ensure_mutable_sequence(ss) for ss in item]
	elif isinstance(item, number):
		return item
	else:
		raise Exception('Not supported yet', item)


def maybe_get_tuple_of_integers(item):
	#TODO - add more checks and also allow for rule based extension
	if isinstance(item, tuple):
		if all(isinstance(i, integer) for i in item):
			return item


import sys
class subscope:
	to_export = None

	def __enter__(self):
		assert self.to_export is None
		self.to_export = dict(sys._getframe(1).f_locals)
		return self

	def __exit__(self, et, ev, tb):
		target = sys._getframe(1).f_locals
		keys = set(target)

		for key, value in self.to_export.items():
			keys.discard(key)
			target[key] = value

		for key in keys:	#Discard remaining
			del target[key]

		self.to_export = None

	def export(self, name, value):
		self.to_export[name] = value


class OP:
	op = register_symbol('math.operation')

	negate = op()
	invert = op()

	add = op()
	subtract = op()

	multiply = op()
	divide = op()

	power = op()


def space_wrap(item):
	result = str(item)
	if ' ' in result:
		return f'({result})'
	else:
		return result

class space_wrapping_object_accessor(Mapping):
	def __init__(self, target):
		self.target = target

	class builtin_formatters:
		def format_operands(target, operands):
			return space_wrap(', '.join(str(op) for op in operands))

		def format_container(target, *contents):
			formatted_contents = ', '.join(map(str, contents))
			return f'{target.__class__.__name__}({formatted_contents})'

		def format_joined(target, separator, *contents):
			return separator.join(map(str, contents))


	def __getitem__(self, key):
		MISS = object()
		if key == '_':
			return self.target

		elif builtin := getattr(self.builtin_formatters, key, None):
			return types.MethodType(builtin, self.target)

		elif (value := getattr(self.target, key, MISS)) is not MISS:
			return space_wrap(value)

		elif key in get_fields(self.target.__class__):
			return '?'
		else:
			raise AttributeError(represent_local_fields(self.target), key)

	def __iter__(self):
		yield from get_fields(self.target.__class__)

	def __len__(self):
		return len(get_fields(self.target.__class__))



#  ___
# | _ ) __ _ ___ ___ ___
# | _ \/ _` (_-</ -_|_-<
# |___/\__,_/__/\___/__/

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

	with subscope() as ss:
		bin_ops = dict(
			add = 		OP.add,
			sub = 		OP.subtract,
			mul = 		OP.multiply,
			truediv = 	OP.divide,
			pow = 		OP.power,
		)

		for name, op in bin_ops.items():
			ss.export(f'__{name}__', pending_operation_factory(op))
			ss.export(f'__r{name}__', pending_operation_factory(op))

	__neg__ = pending_operation_factory(OP.negate)


	def __repr__(self):
		return eval(f'f{self.format!r}', {}, space_wrapping_object_accessor(self))


class operation(base):
	pass

class unary_operation(operation):
	pass

# class binary_operation(operation):
# 	pass

class nary_operation(operation):
	operands = RTS.all_positional()

class primitive_token(base):
	pass

class function_base(base):
	operands = RTS.all_positional()
	format = '{format_container(*_.operands)}'


#  ___     _       _ _   _           _____    _
# | _ \_ _(_)_ __ (_) |_(_)_ _____  |_   _|__| |_____ _ _  ___
# |  _/ '_| | '  \| |  _| \ V / -_)   | |/ _ \ / / -_) ' \(_-<
# |_| |_| |_|_|_|_|_|\__|_|\_/\___|   |_|\___/_\_\___|_||_/__/

class symbol(primitive_token):
	name = RTS.positional()
	format = '{name}'

class constant(primitive_token):
	name = RTS.positional()
	numerical_value = RTS.positional()
	format = '{name}'

#  _   _                       ___                     _   _
# | | | |_ _  __ _ _ _ _  _   / _ \ _ __  ___ _ _ __ _| |_(_)___ _ _  ___
# | |_| | ' \/ _` | '_| || | | (_) | '_ \/ -_) '_/ _` |  _| / _ \ ' \(_-<
#  \___/|_||_\__,_|_|  \_, |  \___/| .__/\___|_| \__,_|\__|_\___/_||_/__/
#                      |__/        |_|

class negate(unary_operation):
	operand = RTS.positional()
	format = '-{operand}'

class reciprocal(unary_operation):
	operand = RTS.positional()
	format = '{operand}⁻¹'

#  ___ _                       ___                     _   _
# | _ |_)_ _  __ _ _ _ _  _   / _ \ _ __  ___ _ _ __ _| |_(_)___ _ _  ___
# | _ \ | ' \/ _` | '_| || | | (_) | '_ \/ -_) '_/ _` |  _| / _ \ ' \(_-<
# |___/_|_||_\__,_|_|  \_, |  \___/| .__/\___|_| \__,_|\__|_\___/_||_/__/
#                      |__/        |_|


# class power(binary_operation):
# 	base = RTS.positional()
# 	exponent = RTS.positional()
# 	format = '{base} ** {exponent}'

#  _  _                      ___                     _   _
# | \| |___ __ _ _ _ _  _   / _ \ _ __  ___ _ _ __ _| |_(_)___ _ _  ___
# | .` |___/ _` | '_| || | | (_) | '_ \/ -_) '_/ _` |  _| / _ \ ' \(_-<
# |_|\_|   \__,_|_|  \_, |  \___/| .__/\___|_| \__,_|\__|_\___/_||_/__/
#                    |__/        |_|


with subscope() as ss:
	operations_lut = dict(
		add = 		'+',
		subtract = 	'-',
		multiply = 	'*',
		divide = 	'/',
		power = 	'**',
	)

	for name, separator in operations_lut.items():
		ss.export(name, type(name, (nary_operation,), dict(
			format = f'{{format_joined(" {separator} ", *_.operands)}}'
		)))


#  ___             _   _
# | __|  _ _ _  __| |_(_)___ _ _  ___
# | _| || | ' \/ _|  _| / _ \ ' \(_-<
# |_| \_,_|_||_\__|\__|_\___/_||_/__/

class function:
	with subscope() as ss:
		known_functions = 'sin cos tan asin acos atan atan2 isin icos itan exp sqrt cbrt log log2 log10 logn'.split()
		for function_name in known_functions:
			ss.export(function_name, type(function_name, (function_base,), {}))

	class sum(nary_operation):
		operands = RTS.all_positional()
		format = '\N{greek capital letter sigma} {format_operands(_.operands)}'

	class product(nary_operation):
		operands = RTS.all_positional()
		format = '\N{greek capital letter pi} {format_operands(_.operands)}'

#   ___             _            _
#  / __|___ _ _  __| |_ __ _ _ _| |_ ___
# | (__/ _ \ ' \(_-<  _/ _` | ' \  _(_-<
#  \___\___/_||_/__/\__\__,_|_||_\__/__/

class constant:
	pi = constant('\N{greek small letter pi}', math.pi)
	tau = constant('\N{greek small letter tau}', math.tau)
	e = constant('e', math.e)


#   ___                        _ _      ___  _     _        _
#  / __|___ _ __  _ __  ___ __(_) |_   / _ \| |__ (_)___ __| |_ ___
# | (__/ _ \ '  \| '_ \/ _ (_-< |  _| | (_) | '_ \| / -_) _|  _(_-<
#  \___\___/_|_|_| .__/\___/__/_|\__|  \___/|_.__// \___\__|\__/__/
#                |_|                            |__/


DEFAULT_ORDER = object()	#TODO - register proper symbol

class matrix(base):
	sub_elements = RTS.all_positional()
	ordering = RTS.setting(DEFAULT_ORDER)	#TODO - define what this means (it will probably mean row-major but extending to more dimensions
	dimensional_names = RTS.setting(None)

	format = f'{{format_joined(", ", *_.sub_elements)}}'

	def serialize(self):
		return tuple(self[c] for c in self.iter_serial_coordinates())

	def ensure_mutability(self):
		self.sub_elements = ensure_mutable_sequence(self.sub_elements)


	def apply_serial_data(self, data):
		self.ensure_mutability()
		coords = tuple(self.iter_serial_coordinates())

		assert len(coords) == len(data)
		for c, v in zip(coords, data):
			self[c] = v

	@property
	def dimensionality(self):
		return len(self.dimensions)

	def get_traversal_order(self):
		if self.dimensional_names:
			dimension_id_by_name = {n: d for d, n in enumerate(self.dimensional_names)}
		else:
			dimension_id_by_name = {}

		dimension_by_id = self.dimensions

		ordering = self.ordering
		if ordering is DEFAULT_ORDER:
			ordering = range(self.dimensionality)

		return tuple(dimension_id_by_name.get(order_dim_id, order_dim_id) for order_dim_id in ordering)

	def iter_serial_coordinates(self):
		dimensions = self.dimensions
		dimensionality = len(dimensions)
		traversal_order = self.get_traversal_order()

		def iter_coordinates(dimension_order_index=0, coordinate={}):
			t_dim = traversal_order[dimension_order_index]
			pending_dimension_order_index = dimension_order_index + 1
			for index in range(dimensions[t_dim]):
				local_coordinate = {**coordinate, t_dim: index}
				if pending_dimension_order_index < dimensionality:
					yield from iter_coordinates(pending_dimension_order_index, local_coordinate)
				else:
					yield tuple(local_coordinate[ci] for ci in range(dimensionality))

		yield from iter_coordinates()



	@property
	def dimensions(self):
		dimensions = dict()

		def count(dim, item):
			nonlocal dimensions

			if isinstance(item, (tuple, list)): 	#TODO - abc
				length = len(item)
				if (existing := dimensions.get(dim)) is not None:
					assert existing == length
				else:
					dimensions[dim] = length

				for sub_element in item:
					count(dim + 1, sub_element)

		count(0, self.sub_elements)

		return tuple(dimensions.values())	#Ordering is assured by how count() operates



	def __getitem__(self, slice):
		if coordinate := maybe_get_tuple_of_integers(slice):
			assert len(coordinate) == self.dimensionality
			ref = self.sub_elements
			for c in coordinate:
				ref = ref[c]
			return ref


		elif slicing := maybe_get_tuple_of_intervals(slice):
			print('INTERVALS', slicing)
			raise Exception()
		else:
			raise Exception()



	def __setitem__(self, slice, value):
		if coordinate := maybe_get_tuple_of_integers(slice):
			assert len(coordinate) == self.dimensionality
			ref = self.sub_elements
			li = len(coordinate) - 1
			for c in coordinate[:-1]:
				ref = ref[c]

			ref[coordinate[-1]] = value




		elif slicing := maybe_get_tuple_of_intervals(slice):
			print('INTERVALS', slicing)
			raise Exception()
		else:
			raise Exception()


	def ascii_format(self):
		#TODO - these features should probably be its own module
		class L:
			T, M, B = '⎡⎢⎣'
		class R:
			T, M, B = '⎤⎥⎦'

		if self.dimensionality == 1:
			return ascii_format_vector(self.sub_elements).wrap('[]')
		elif self.dimensionality == 2:
			row_formats = tuple(map(ascii_format_vector, self.sub_elements))
			for rf in row_formats:
				print(rf.minimum_size)

			pass
		else:
			raise Exception('Not Implemented')

#  ___     _                        _ _      _          ___  _     _        _
# |_ _|_ _| |_ ___ _ _ _ __  ___ __| (_)__ _| |_ ___   / _ \| |__ (_)___ __| |_ ___
#  | || ' \  _/ -_) '_| '  \/ -_) _` | / _` |  _/ -_) | (_) | '_ \| / -_) _|  _(_-<
# |___|_||_\__\___|_| |_|_|_\___\__,_|_\__,_|\__\___|  \___/|_.__// \___\__|\__/__/
#                                                               |__/

class pending_operation(base):
	operation = RTS.positional()
	operands = RTS.all_positional()
	format = '{format_container(_.operation, *_.operands)}'

