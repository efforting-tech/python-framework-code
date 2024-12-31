from .. import records as R
from . import Indention, Token, NEW_LINE

import re

#NOTE - currently indent is assuming tabulators. Lineref should refer to document for indention

class Line_Reference(R.Record):
	document: R.Field()
	index: R.Field()
	start: R.Field()
	end: R.Field()


	@property
	def first_token(self):
		if self.start > self.end:
			return

		return self.document.tokens[self.start]

	@property
	def last_token(self):
		if self.start > self.end:
			return

		return self.document.tokens[self.end]

	@property
	def tokens(self):
		return self.document.tokens[self.start:self.end+1]

	def __len__(self):
		return self.end - self.start + 1

	@property
	def first_non_indent_token(self):
		match self.first_token:
			case Indention(match=re.Match() as match) if self.start + 1 <= self.end:
				return self.document.tokens[self.start + 1]

			case non_indent:
				return non_indent

	def text_from_tokens(self):
		#This function is mostly useful to verify that there are no lost or repeated tokens - I leave it here for now
		#but we may want to move it to a test once we start using unit testing
		return ''.join(t.match.group(0) for t in self.tokens)

	@property
	def text(self):
		l, r = self.span
		return self.document.text[l:r]

	@property
	def span(self):
		#Note that first and last may be the same
		first = self.tokens[0]
		last = self.tokens[-1]
		return first.match.start(), last.match.end()


	@property
	def indent_match(self):
		match self.first_token:
			case Indention(match=re.Match() as match):
				return match

	@property
	def indent(self):
		match self.first_token:
			case Indention(match=re.Match() as match):
				return match.group()

			case Token() as token if token.type is NEW_LINE:
				return None	#No content

			case unhandled:
				return ''	#No indention



	@property
	def body_span(self):
		'Skips indention and newline'

		match self.first_token:
			case Indention(match=re.Match() as match) if self.start + 1 <= self.end:
				first = self.start + 1

			case non_indent:
				first = self.start

		#Currently we can have 0 or 1 newline at the end of a line, not more
		match self.last_token:
			case Token(match=re.Match() as match) as token if token.type is NEW_LINE:
				last = self.end - 1

			case no_newline:
				last = self.end

		if first <= last:
			return first, last

	@property
	def body_tokens(self):
		if span := self.body_span:
			first, last = span
			return self.document.tokens[first:last+1]

	@property
	def body_text(self):
		if span := self.body_span:
			first, last = span
			l, r = self.document.tokens[first].match.start(), self.document.tokens[last].match.end()
			return self.document.text[l:r]


