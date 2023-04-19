from .. import type_system as RTS
from .. import abstract_base_classes as ABC

#DEPRECATE in favor of priority_translator
@ABC.register_class_tree('internal.action')
class action:
	__init__ = RTS.initialization.standard_fields
	__repr__ = RTS.representation.local_fields


class return_value(action):
	value = RTS.positional()

	def __call__(self, match):
		return self.value


class return_match(action):

	def __call__(self, match):
		return match

class return_matched_value(action):
	def __call__(self, match):
		return match.get_value()

class process_matched_value(action):
	function = RTS.positional()

	def __call__(self, match):
		return self.function(match.get_value())
