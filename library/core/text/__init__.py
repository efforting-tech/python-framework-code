import dataclasses as DCL
import re

@DCL.dataclass
class Token:
	match: re.Match

@DCL.dataclass
class Document:
	tokens: tuple[Token]

@DCL.dataclass
class Line_Index_Entry:
	start: int
	end: int

	@property
	def count(self):
		return self.end - self.start + 1

@DCL.dataclass
class Line_Index:
	lines: tuple[Line_Index_Entry]



