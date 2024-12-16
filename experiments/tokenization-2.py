from tokenization_common import split_tokens_into_lines, value_to_color_spiral, freeze, Indention, template_tokenizer, NEW_LINE, Token
from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import ABC

import re

#In this experiment we will investigate how we can turn this into a tree
#We will also identify lines that represent statements - this will be different from our traditional regex based criteria since we must check the first token of the line

text = '''

	Hello World! Here is the <<== inline expression ==>>!
	This is a <<==! literal thing
\t
	##==! Not a statement

	##== IS as a statement
		with a body too

'''


@ABC.Factory.Contextual
class Bound_Factory(R.Record):
	factory: R.Field()

	def __call__(self, context):
		return self.factory(context['instance'])

class Document(R.Record):
	text: R.Field(repr=False)
	tokens: R.Field(repr=False, factory=Bound_Factory(
		lambda self: self.tokenizer.tokenize(self.text).tokens
	))
	lines: R.Field(repr=False, factory=Bound_Factory(
		lambda self: tuple(split_tokens_into_lines(self.tokens, preserve_ends=True))
	))
	tokenizer: R.Field() = template_tokenizer


	def __iter__(self):
		for l, r in self.lines:
			yield Line_Reference(self, l, r)

class Line_Reference(R.Record):
	document: R.Field()
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

	@property
	def body(self):
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
			l, r = self.document.tokens[first].match.start(), self.document.tokens[last].match.end()
			return self.document.text[l:r]





for line in Document(text):
	print(line.first_non_indent_token, repr(line.indent), repr(line.body))
