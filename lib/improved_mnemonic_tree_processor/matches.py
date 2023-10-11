from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_processing.tokenization import extract_positionals_and_keyword_arguments_from_match

class matched_condition(public_base):
	condition = RTS.positional()
	item = RTS.positional()
	match = RTS.positional()

class matched_regex(public_base):
	condition = RTS.positional()
	match = RTS.positional()	#match contains the item

	@property
	def item(self):
		return self.match.string

	@property
	def as_dict(self):
		pos, named = extract_positionals_and_keyword_arguments_from_match(self.match)
		return named

	@property
	def as_arguments(self):
		return extract_positionals_and_keyword_arguments_from_match(self.match)

class matched_value(public_base):
	condition = RTS.positional()
	item = RTS.positional()

class matched_unconditionally(public_base):
	item = RTS.positional()
