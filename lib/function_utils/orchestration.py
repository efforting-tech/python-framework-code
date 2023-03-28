
from .. import rudimentary_type_system as RTS

class call_sequence:
	sequence = RTS.all_positional()

	__init__ = RTS.initialization.standard_fields
	__repr__ = RTS.representation.local_fields

	def __call__(self, *positional, **named):
		for function in self.sequence:
			function(*positional, **named)

