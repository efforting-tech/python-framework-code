from .types import base, UNDEFINED
from .. import rudimentary_type_system as RTS
from .. development_utils import cde #TODO import from proper place
from .utils import ensure_mutable_sequence, maybe_get_tuple_of_integers
from . import operations

DEFAULT_ORDER = object()	#TODO - register proper symbol
DEFAULT = object()

#TODO - harmonize with vector - use APIs - use interfaces - use common grounds


class matrix(base):
	sub_elements = RTS.all_positional()
	ordering = RTS.setting(DEFAULT_ORDER)	#TODO - define what this means (it will probably mean row-major but extending to more dimensions
	dimensional_names = RTS.setting(None)	#TODO - support a dict here where we for each dimension also specify names for the elements (useful for swizzling)

	format = '{format_joined(", ", *_.sub_elements)}'

	@RTS.initializer
	def init(self):
		#Here we should unpack any vectors in sub_elements
		#self.consistency_check()
		pass



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
		#TODO - these features should probably be its own formatting module
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

	#Requirement - empty must be synchronized with __init__. We don't use double star notation because that makes it harder to follow the code
	@classmethod
	def empty(cls, *dimensions, place_holder=UNDEFINED, ordering=DEFAULT, dimensional_names=DEFAULT):


		#TODO - dimensions should support integers, sequence of names or vectors

		def create_contents(dim):
			match dim:
				case [d]:
					return d * (place_holder,)
				case [d, *remaining]:
					return (create_contents(remaining),) * d


		return cls(
			*create_contents(dimensions),
			**cde(ordering is not DEFAULT, ordering=ordering),	#TODO - make some nice generic function for this purpose
			**cde(dimensional_names is not DEFAULT, dimensional_names=dimensional_names),
		)


	@property
	def dimension_by_name(self):
		return {name: index for index, name in enumerate(self.dimensional_names)}


	def __iter__(self):
		yield from self.sub_elements

	def __getattr__(self, key):

		if key in self.dimension_by_name:
			return matrix_axis(self, key)


		chars = set(key)
		if chars & set(self.get_swizzle_names()) == chars:
			return operations.swizzle(self, key)
		else:
			raise AttributeError(self, key)

	def __setattr__(self, key, value):
		chars = set(key)
		if chars & set(self.get_swizzle_names()) == chars:
			operations.swizzle(self, key).set(value)
		else:
			super().__setattr__(key, value)
		#raise AttributeError(self, key)



	def get_swizzle_names(self):	#TODO - connect to swizzle API

		#We need to decide the API for this since we are referring to dimensional names
		#We should figure out the difference between matrices, vectors and named axis in matrices
		#Matrices may have named entries in different dimensionality

		result = dict()
		if self.dimensional_names and isinstance(self.dimensional_names, dict):
			for axis, names in self.dimensional_names.items():
				for index, n in enumerate(names):
					result[n] = matrix_slice(self, axis, index, alias=n)

		return result

class matrix_axis(base):
	matrix = RTS.positional()
	axis = RTS.positional()

	format = '{matrix}.{axis}'

	#def __getitem__(self):


class matrix_slice(base):
	matrix = RTS.positional()
	axis = RTS.positional()
	index = RTS.positional()
	alias = RTS.field(default=None)	#Useful to keep track of swizzle

	format = '{matrix}.{axis}[{index}]'
