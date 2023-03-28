#Here we are testing more IMS types
from ims_types import *


#  _____       _   _
# |_   _|__ __| |_(_)_ _  __ _
#   | |/ -_|_-<  _| | ' \/ _` |
#   |_|\___/__/\__|_|_||_\__, |
#                        |___/

#Define a bunch of assortment rack layouts
arls = dict(
	blue = 		grid_layout.from_string('	9x4 	1x1				'),
	wood21 = 	grid_layout.from_string('	1x2 	1x1				'),
	wood31 = 	grid_layout.from_string('	3x1						'),
	wood33 = 	grid_layout.from_string('	3x3						'),
	wood32 = 	grid_layout.from_string('	1x3		2x1				'),
	toolcab = 	grid_layout.from_string('	6x1						'),
	small = 	grid_layout.from_string('	4x2						'),
	abstack = 	grid_layout.from_string('	4x1						'),
	large8sr = 	grid_layout.from_string('	8x5 	1x4		1x1		'),
	large12sr = grid_layout.from_string('	12x5					'),
)


l = arls['blue']	#We will use the blue one
ar1 = container(l, tuple(container_cell(v) for v in l.iter_slot_indices()))

#Define some items
capacitor = item_definition('capacitor')
slime = item_definition('slime')
junk = item_definition('junk')
elephant = item_definition('elephant')

#Populate one of the drawers
drawer = ar1.contents[0]
drawer.contents.append(sku_amount(capacitor, measure(10, U.count)))
drawer.contents.append(sku_amount(slime, measure(5, U.micro_l)))
drawer.contents.append(sku_amount(junk, measure(2.3, U.kton)))
drawer.contents.append(sku_amount(elephant, measure(2, U.doz)))
