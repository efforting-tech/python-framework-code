from efforting.mvp4.presets.text_processing import *

#To decide - should the type be part of the field? Should a field be a type or not?


class enumeration(public_base):
	values = RTS.all_positional()
	namespace = RTS.optional_factory(symbol_node)
	map = RTS.factory(dict)

	@RTS.initializer
	def init(self):


		for name in self.values:
			match name:
				case str():
					symbol = self.namespace.create_symbol(name)
					self.map[name] = symbol


				case (name, *alias_list):
					symbol = self.namespace.create_symbol(name)

					for n in (name, *alias_list):
						self.map[n] = symbol

				case _ as value:
					raise Exception(value)



class discrete_vector(public_base):
	size = RTS.positional()
	selection = RTS.positional()
	names = RTS.field(default=None)

	def __call__(self, *components):
		return discrete_vector_instance(self, *components)

class integer_vector(public_base):
	size = RTS.positional()
	names = RTS.field(default=None)

	def __call__(self, *components):
		return integer_vector_instance(self, *components)



class discrete_vector_instance(public_base):
	vector = RTS.positional()
	components = RTS.all_positional()

	@RTS.initializer
	def _initial_expansion(self):
		#TODO - initial expansion
		assert self.vector.size == len(self.components)

class integer_vector_instance(public_base):
	vector = RTS.positional()
	components = RTS.all_positional()

	@RTS.initializer
	def _initial_expansion(self):
		#TODO - initial expansion
		assert self.vector.size == len(self.components)


grid_coordinate = integer_vector(2, ('row', 'column'))
print(grid_coordinate(10, 20))





# class segmentation(public_base, abstract=True):
# 	pass

# class axis_segmentation(segmentation):
# 	count = RTS.positional()

# class layout(public_base, abstract=True):
# 	pass

# grid_size = integer_vector('rows', 'columns')

# class grid_layout(layout):
# 	size = RTS.positional(type=grid_size)