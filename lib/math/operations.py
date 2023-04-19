from .types import unary_operation, nary_operation, operation
from ..data_utils import subscope
from .. import type_system as RTS

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


#  _  _                      ___                     _   _
# | \| |___ __ _ _ _ _  _   / _ \ _ __  ___ _ _ __ _| |_(_)___ _ _  ___
# | .` |___/ _` | '_| || | | (_) | '_ \/ -_) '_/ _` |  _| / _ \ ' \(_-<
# |_|\_|   \__,_|_|  \_, |  \___/| .__/\___|_| \__,_|\__|_\___/_||_/__/
#                    |__/        |_|

with subscope() as ss:
	operations_lut = dict(
		add = 						'+',
		subtract = 					'-',
		multiply = 					'*',
		divide = 					'/',
		power = 					'**',

		equal = 					'=',
		not_equal = 				'≠',

		greater_than = 				'>',
		less_than = 				'<',
		greater_than_or_equal = 	'≥',
		less_than_or_equal = 		'≤',

		belongs_to = 				'∈',

	)

	for name, separator in operations_lut.items():
		ss.export(name, type(name, (nary_operation,), dict(
			format = f'{{format_joined(" {separator} ", *_.operands)}}'
		)))


class swizzle(operation):
	reference = RTS.positional()
	fields = RTS.positional()
	format = '{reference}.{fields}'

	def __iter__(self):
		d = {v: i for i, v in enumerate(self.reference.get_swizzle_names())}
		yield from tuple(self.reference[d[f]] for f in self.fields)	#We must store in a tuple here so r.abc = r.bac can work


	def set(self, values):
		d = {v: i for i, v in enumerate(self.reference.get_swizzle_names())}
		for f, v in zip(self.fields, values):
			self.reference[d[f]] = v
