from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol

from .sequence_resolver import sequence_delta_resolver


class unordered_dict_operation:
	class update(public_base):
		items = RTS.field()

	class delete(public_base):
		items = RTS.field()

class ordered_dict_operation:
	class delta(public_base):
		key_delta = RTS.field()
		value_delta = RTS.field()


MISS = register_symbol('MISS')	#TODO import from proper place

class unordered_dict_delta_resolver(public_base):
	include_delete = RTS.setting(True)

	def resolve_delta(self, s1, s2):
		updates = set()
		for key in s2:
			v1, v2 = s1.get(key, MISS), s2[key]

			if (v1 is MISS) or (v1 != v2):
				updates.add(key)

		if self.include_delete:
			yield unordered_dict_operation.delete(set(s1) - set(s2))

		if updates:
			yield unordered_dict_operation.update(updates)


class ordered_dict_delta_resolver(public_base):
	key_resolver = RTS.factory(sequence_delta_resolver)
	value_resolver = RTS.factory(unordered_dict_delta_resolver, include_delete=False)

	def resolve_delta(self, s1, s2):
		yield ordered_dict_operation.delta(
			tuple(self.key_resolver.resolve_delta(tuple(s1.keys()), tuple(s2.keys()))),
			tuple(self.value_resolver.resolve_delta(s1, s2)),
		)