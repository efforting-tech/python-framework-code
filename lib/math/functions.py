from ..data_utils import subscope as _subscope

with _subscope() as ss:
	from .types import function
	from .. import type_system as RTS

	known_functions = 'sin cos tan asin acos atan atan2 isin icos itan exp sqrt cbrt log log2 log10 logn'.split()
	for function_name in known_functions:
		ss.export(function_name, type(function_name, (function,), {}))

	class sum(function):
		operands = RTS.all_positional()
		format = '\N{greek capital letter sigma} {format_operands(_.operands)}'

	class product(function):
		operands = RTS.all_positional()
		format = '\N{greek capital letter pi} {format_operands(_.operands)}'
