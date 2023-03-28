from efforting.mvp4.presets.text_processing import *
from grid_layout import create_grid_from_string
import functools
import types


#Note - there is a difference in different layout instances, it could either be that all cells are sublayout (including a single slot which is denoted by None)
#		or the cells are whatever can be put in a layout.


'''


𝔸 layout
	𝕋 grid
		ℕ 	rows, columns

	𝕋 instance
		→ layout				layout
		layout?[]				contents

		# (layout | None)[]


	We should figure out how to properly depict typing

'''





def assert_exhausted(*iterator_list):
	for iterator in iterator_list:
		try:
			next(iterator)
			assert False, f'iterator {iterator} not exhausted'
		except StopIteration:
			pass


class creation_interface(public_base):
	function = RTS.field()

	def __get__(self, instance, owner):
		return types.MethodType(self.function, owner)

class instancing_interface(public_base):
	type = RTS.field()

	def __get__(self, instance, owner):
		if instance is None:
			return self
		else:
			return functools.partial(self.type, instance)


class db_field(RTS.field):
	pass

class layout_instance(public_base):
	layout = RTS.field()
	contents = RTS.field()

	def iter_slot_indices(self):
		viter = iter(self.contents)
		vslots = self.layout.iter_slot_indices()
		for gref, value in zip(vslots, viter):
			match value:
				case grid_layout():
					for sub_gref in value.iter_slot_indices():
						yield sub_reference(gref, sub_reference)
				case _:
					raise Exception(value)

		assert_exhausted(viter, vslots)

		#for row, col in itertools.product(range(self.rows), range(self.columns)):
			#yield grid_reference(self, row, col)


class sub_reference(public_base):
	parent_reference = db_field()
	sub_reference = db_field()

class grid_layout(public_base):
	rows = db_field()
	columns = db_field()
	owner = db_field()

	from_string = creation_interface(create_grid_from_string)

	def iter_slot_indices(self):
		for row, col in itertools.product(range(self.rows), range(self.columns)):
			yield grid_reference(self, row, col)


	__call__ = instancing_interface(layout_instance)


class grid_reference(public_base):
	grid = RTS.positional()
	row = RTS.positional()
	column = RTS.positional()
