from ... import type_system as RTS
from ...type_system.bases import public_base

class non_reversible:
	class insert(public_base):
		position = RTS.positional()
		sequence = RTS.positional()

	class delete(public_base):
		position = RTS.positional()
		length = RTS.positional()

	class replace(public_base):
		position = RTS.positional()
		length = RTS.positional()
		sequence = RTS.positional()

class reversible:
	class insert(public_base):
		position = RTS.positional()
		sequence = RTS.positional()

	class delete(public_base):
		position = RTS.positional()
		deleted = RTS.positional()

	class replace(public_base):
		position = RTS.positional()
		replaced = RTS.positional()
		sequence = RTS.positional()
