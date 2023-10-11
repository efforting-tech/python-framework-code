import re

from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_processing.command_pattern_processor import command_pattern_processor

from . import matches as M


class match_interface:
	pass
	#TODO: check_match abstract method


class title_condition(public_base, match_interface):
	condition = RTS.positional()

	def check_match(self, item):
		if match := self.condition.check_match(item.title):
			return M.matched_condition(self, item, match)

class matches_regex(public_base, match_interface):
	pattern = RTS.positional(read_only=True)

	@RTS.cached_property(pattern)
	def regex_pattern(self):
		return re.compile(self.pattern)

	@RTS.cached_property(pattern)
	def regex_captures(self):
		return tuple(self.regex_pattern.groupindex)

	def check_match(self, item):
		if isinstance(item, str) and (match := self.regex_pattern.match(item)):
			return M.matched_regex(self, match)

	def search(self, text, pos=0):
		return self.regex_pattern.search(text, pos)

class matches_literal(public_base, match_interface):
	value = RTS.positional(read_only=True)

	@RTS.cached_property(value)
	def regex_pattern(self):
		return re.compile(re.escape(self.value))

	def check_match(self, item):
		if item == self.value:
			return M.matched_value(self, item)

	def search(self, text, pos=0):
		return self.regex_pattern.search(text, pos)

class matches_identity(public_base, match_interface):
	identity = RTS.positional()

	def check_match(self, item):
		if item is self.identity:
			return M.matched_value(self, item)

class instance_of(public_base, match_interface):
	type = RTS.positional()

	def check_match(self, item):
		if isinstance(item, self.type):
			return M.matched_value(self, item)


class matches_type_identity(public_base, match_interface):
	identity = RTS.positional()

	def check_match(self, item):
		if type(item) is self.identity:
			return M.matched_value(self, item)


class matches_mnemonic(public_base, match_interface):
	mnemonic = RTS.positional(read_only=True)

	@RTS.cached_property(mnemonic)
	def mnemonic_pattern(self):
		return command_pattern_processor(self.mnemonic)

	@RTS.cached_property(mnemonic)
	def regex_pattern(self):
		return re.compile(f'^{self.mnemonic_pattern.to_pattern()}$')

	@RTS.cached_property(mnemonic)
	def mnemonic_captures(self):
		return tuple(self.mnemonic_pattern.iter_captures())

	@RTS.cached_property(mnemonic)
	def regex_captures(self):
		return tuple(self.regex_pattern.groupindex)

	def search(self, text, pos=0):
		return self.regex_pattern.search(text, pos)

	def check_match(self, item):
		if isinstance(item, str) and (match := self.regex_pattern.match(item)):
			return M.matched_regex(self, match)