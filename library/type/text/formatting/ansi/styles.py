from .....record.base.public import Structure
from .....record import member as M

class ANSI_Style(Structure):
	bgc_lut = M.positional(factory=dict)
	fgc_lut = M.positional(factory=dict)
	flag_lut = M.positional(factory=dict)

default = ANSI_Style(
	bgc_lut = {
		'red': ('41', '49'),
		'green': ('42', '49'),
		'brown': ('43', '49'),
		'blue': ('44', '49'),
		'magenta': ('45', '49'),
		'cyan': ('46', '49'),
		'gray': ('47', '49'),
		'grey': ('47', '49'),
	},

	fgc_lut = {
		'red': ('31', '39'),
		'green': ('32', '39'),
		'brown': ('33', '39'),
		'blue': ('34', '39'),
		'magenta': ('35', '39'),
		'cyan': ('36', '39'),
		'gray': ('37', '39'),
		'grey': ('37', '39'),

		'bright-red': ('31;1', '22;39'),
		'bright-green': ('32;1', '22;39'),
		'yellow': ('33;1', '22;39'),
		'bright-blue': ('34;1', '22;39'),
		'hot-pink': ('35;1', '22;39'),
		'bright-cyan': ('36;1', '22;39'),
		'white': ('37;1', '22;39'),

		'dark-red': ('31;2', '22;39'),
		'dark-green': ('32;2', '22;39'),
		'dark-yellow': ('33;2', '22;39'),

	},

	flag_lut = {
		'bold': ('1', '22'),
		'faint': ('2', '22'),
		'italics': ('3', '23'),
		'underline': ('4', '24'),
		'invert': ('7', '27'),
		'strikethrough': ('9', '29'),

	}

)

