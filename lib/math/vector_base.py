from .types import base, UNDEFINED, scalar
from .. import rudimentary_type_system as RTS
from .utils import get_main_math_type
from .. development_utils import cde #TODO import from proper place
from . import operations
from .utils import ensure_mutable_sequence

import typing

#TODO - harmonize with matrix - use APIs - use interfaces - use common grounds


class vector(base):
	sub_elements = RTS.all_positional()
	name = RTS.field(default=None)	#As a named thing this should implement __set_name__ (todo - make interface)
	element_names = RTS.field(default=None)
	format = '{_.name or ""}({format_joined(", ", *_.sub_elements)})'

	@RTS.initializer
	def init(self):
		self.consistency_check()

	def get_swizzle_names(self):	#TODO - connect to swizzle API
		raise Exception()	#make compatible with matrix_base
		return self.element_names

	def consistency_check(self):
		element_types = set(map(get_main_math_type, self.sub_elements))
		assert len(element_types) == 1, f'{self.__class__} is a strict container where all sub elements must have the same type. Current: {self} - {element_types}'

		if self.element_names:
			assert len(self.element_names) == len(self.sub_elements)

	def __len__(self):
		return len(self.sub_elements)

	#Requirement - empty must be synchronized with __init__. We don't use double star notation because that makes it harder to follow the code
	@classmethod
	def empty(cls, *args, place_holder=UNDEFINED, name=UNDEFINED):

		settings = dict(
			**cde(name is not UNDEFINED, name=name),
		)

		match args:
			case [int() as count]:
				return cls(*((place_holder,) * count), **settings)
			case _ if all(isinstance(i, str) for i in args):
				count = len(args)
				return cls(*((place_holder,) * count), element_names=tuple(args), **settings)
			case _:
				raise Exception()

	def __call__(self, *new_elements):
		#Calling a vector will use the current vector as a template for a new
		return self.__class__(*new_elements, element_names=self.element_names, name=self.name)


	def __setitem__(self, index, value):
		self.ensure_mutability()
		self.sub_elements[index] = value

	def __getitem__(self, index):
		return self.sub_elements[index]

	def __iter__(self):
		yield from self.sub_elements

	def __getattr__(self, key):
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


	def ensure_mutability(self):
		self.sub_elements = ensure_mutable_sequence(self.sub_elements)
