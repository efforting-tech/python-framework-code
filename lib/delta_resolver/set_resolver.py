from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol

class set_operation:
	class add(public_base):
		items = RTS.field()

	class delete(public_base):
		items = RTS.field()

	class replace(public_base):
		items = RTS.field()

	operand = register_symbol('internal.delta.set.operand')
	clear = operand('clear')

class set_delta_resolver(public_base):

	def resolve_delta(self, s1, s2):
		added = s2 - s1
		deleted = s1 - s2

		if (len(deleted) + len(added) > (len(s2) * .5)):	#TODO - figure out if this is a reasonable condition
			yield set_operation.replace(s2)

		elif deleted and not s2:
			yield set_operation.clear
		else:
			if added:
				yield set_operation.add(added)

			if deleted:
				yield set_operation.delete(deleted)


