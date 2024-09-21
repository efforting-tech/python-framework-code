from .. import record as R
from ... import ABC

class Regex_Rule(R.Record):
	pattern: R.Field(type=ABC.Regex.Compiled)
	action: R.Field() = True

	def match(self, item):
		return self.pattern.fullmatch(item)
