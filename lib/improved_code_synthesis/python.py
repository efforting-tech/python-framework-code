from .. import type_system as RTS
from ..type_system.bases import public_base

class structure(public_base):
	name = RTS.positional()
	members = RTS.factory(dict)

class structure_member(public_base):
	name = RTS.positional()
	definition = RTS.positional(default=None)
	comment = RTS.positional(default=None)

	all_positionals = RTS.setting(False)
	all_named = RTS.setting(False)

class structure_function(public_base):
	name = RTS.positional()
	arguments = RTS.positional()
	function_body = RTS.positional()
	decorator_list = RTS.positional(default=None)


