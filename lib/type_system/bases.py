from .. import type_system as RTS
import types

class standard_base:
	__repr__ = RTS.representation.local_fields

	def __init_subclass__(cls, abstract=False):
		if abstract:
			cls.__init__ = RTS.initialization.abstract
			cls._from_state = RTS.initialization.abstract
			cls._from_config = RTS.initialization.abstract
		else:
			cls.__init__ = RTS.initialization.standard_fields
			cls._from_state = RTS.initialization.from_state
			cls._from_config = RTS.initialization.from_config

class public_base(standard_base):
	__repr__ = RTS.representation.local_public_fields
