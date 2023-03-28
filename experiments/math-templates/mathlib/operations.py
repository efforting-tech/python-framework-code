from .types import unary_operation, nary_operation
from efforting.mvp4.data_utils import subscope
from efforting.mvp4 import rudimentary_type_system as RTS

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
