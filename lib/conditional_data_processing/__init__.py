from .. import type_system as RTS
from .. import abstract_base_classes as ABC


@ABC.register_class_tree('internal.translator')
class base_translator:
	__init__ = RTS.initialization.standard_fields
	__repr__ = RTS.representation.local_fields


#DEPRECATED - base new version from priority_translator
class translator(base_translator):
	rules = RTS.all_positional()

	def translate(self, item):
		for condition, action in self.rules:
			if m := condition.match(item):
				return action(m)

		raise Exception	#or deal with defaults/fallbacks

class contextual_translator(base_translator):
	context = RTS.positional()
	rules = RTS.all_positional()

