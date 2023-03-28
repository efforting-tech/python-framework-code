#Typing experiments


'''


	check				python							match					candidate

	instance			isinstance(item, type)			type()					(type)
	identity			item is identity				# NOT POSSIBLE			identity
	equality			item == value					value					=value




	list of character

		list[character]
		list(character)
		list of character

		list of optional character


	list of optional {type} → list_of(ET(type) | ET.None)



'''

from t5_conditions import *

#from efforting.mvp4.function_utils.pattern_matching import get_matching_ast
#print(get_matching_ast('(T.item_definition(), T.measure())'))
#print(get_condition_ast('stuff is thing', stuff=SUBJECT, thing=int))

#t = anything | instance_of(int)


#print((nothing | nothing).evaluate(10))

import grid_layout as grid_layout_interface

class grid_layout(public_base):
	rows = RTS.positional()
	columns = RTS.positional()


	def __call__(self, *contents):
		return layout_instance(self, contents)

	from_string = classmethod(grid_layout_interface.create_grid_from_string)

	def count_cells(self):
		return self.rows * self.columns

class layout_instance(public_base):
	layout = RTS.positional()
	contents = RTS.positional()

	def count_cells(self):
		return sum(c.count_cells() for c in self.contents)





# class grid_reference(public_base):
# 	grid_instance = RTS.positional()
# 	row = RTS.positional()
# 	column = RTS.positional()

# 	def resolve(self):
# 		return self.grid_instance

g = grid_layout.from_string('8x5 1x4 1x1')

print(g.count_cells())




# layout = grid_layout(2, 2)

# grid = layout(
# 	1, 2,
# 	3, 4
# )


# print(grid)






# from efforting.mvp4.presets.text_processing import *
# class typing_system(public_base):
# 	root = RTS.factory(symbol_node)
# 	directory = RTS.factory(dict)

# 	def register_type(self, path, condition):
# 		self.directory[self.root.create_symbol(path)] = condition


# ET = typing_system()


# ET.register_type('path.to.type', 'stuff')

# print(ET.directory)


# #print(ET('word'))