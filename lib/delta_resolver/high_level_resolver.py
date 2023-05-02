from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol

from .sequence_resolver import sequence_delta_resolver
from .set_resolver import set_delta_resolver
from .dict_resolver import ordered_dict_delta_resolver, unordered_dict_delta_resolver, unordered_dict_operation

#TODO - we may want a post processing step that for instance can unrwap a delta with only one operation in it
#TODO - we should make it much more clear how we are nesting various delta types and what to expect
#		this is so that we know we will be able to fully restore data based on these nested deltas

class generic_operation:
	class replace(public_base):
		item = RTS.field()

	class delta(public_base):
		delta = RTS.field()

	class dict_delta(public_base):
		updates = RTS.field()

MISS = register_symbol('MISS')	#TODO import from proper place

class generic_delta_resolver(public_base):
	sequence_resolver = RTS.factory(sequence_delta_resolver)
	set_resolver = RTS.factory(set_delta_resolver)
	ordered_dict_resolver = RTS.factory(ordered_dict_delta_resolver)
	unordered_dict_resolver = RTS.factory(unordered_dict_delta_resolver)
	min_sequence_length = RTS.setting(4)

	def resolve_delta(self, s1, s2):

		t1 = type(s1)
		t2 = type(s2)
		if t1 is not t2:
			yield generic_operation.replace(s2)
		else:

			match s1:
				#TODO - ordered_set, unordered_dict, structure, text
				case list() | tuple():
					yield from self.sequence_resolver.resolve_delta(s1, s2)

				case set():
					yield from self.set_resolver.resolve_delta(s1, s2)

				case int():	#TODO - other primitives
					yield generic_operation.replace(s2)

				case str():
					if min(len(s1), len(s2)) < self.min_sequence_length:
						yield generic_operation.replace(s2)
					elif '\n' in s1 or '\n' in s2:		#TODO - other ways to check newlines? windows newlines?
						raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
					else:
						yield generic_operation.delta(tuple(self.sequence_resolver.resolve_delta(s1, s2)))

				case bytes():
					if min(len(s1), len(s2)) < self.min_sequence_length:
						yield generic_operation.replace(s2)
					elif b'\n' in s1 or b'\n' in s2:	#TODO - other ways to check newlines? windows newlines?
						raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
					else:
						yield generic_operation.delta(tuple(self.sequence_resolver.resolve_delta(s1, s2)))

				case dict():
					for delta in self.ordered_dict_resolver.resolve_delta(s1, s2):
						for value_delta in delta.value_delta:
							match value_delta:
								case unordered_dict_operation.update():
									dict_delta = dict()
									for key in value_delta.items:
										v1 = s1.get(key, MISS)
										if v1 is not MISS:
											v2 = s2[key]
											dict_delta[key] = tuple(self.resolve_delta(v1, v2))

									value_delta.items = dict_delta


								case _ as unhandled:
									raise Exception(f'The value {unhandled!r} could not be handled')

						yield delta


				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


