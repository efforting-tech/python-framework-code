from tokenization_common import split_tokens_into_lines, value_to_color_spiral, freeze, Indention, template_tokenizer, NEW_LINE, Token
from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import ABC, Symbol as S

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

	def __len__(self):
		return len(self.lines)

	def __getitem__(self, index):
		l, r = self.lines[index]
		return Line_Reference(self, l, r)

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


class Tree_Reference(R.Record):
	document: R.Field()
	first_line: R.Field() = 0
	last_line: R.Field(factory='_init_last_line')
	base_indent: R.Field(factory='get_min_indent')	#Note that order here matters since some of these requires others
	children: R.Field(factory='_init_children')
	indention_mode: R.Field() = S.Indention_Mode.Tabulators

	def _init_last_line(self):
		return len(self.document) - 1

	def _init_children(self):
		base_indent = self.base_indent

		result = list()
		last_index = self.first_line
		#last_index = next(self.iter_lines(False))[0]	#TODO - handle StopIteration

		def add_chunk(index):
			nonlocal last_index
			if (last_index, index) == (self.first_line, self.last_line):
				return
			print('Add chunk', last_index, index, '..', self.first_line, self.last_line)
			result.append(Tree_Reference(self.document, last_index, index))
			last_index = index

		for index, line in self.iter_lines(True):
			indent = self.compute_indent(index)
			if indent == base_indent:
				add_chunk(index)

		#Adding the tail causes infinite recursion now, we might need to guard it
		add_chunk(self.last_line)

		return tuple(result)


	def iter_lines(self, only_with_content=False):
		for index in range(self.first_line, self.last_line - self.first_line + 1):
			line = self.document[index]
			if only_with_content and not line.body_span:
				continue
			yield (index, line)

	@property
	def title(self):
		if body_text := self.document[self.first_line].body_text:
			return body_text.strip()

	@property
	def title_line(self):
		return self.document[self.first_line]

	@property
	def title_indent(self):
		return compute_indent(self.first_line)

	def compute_indent(self, index):
		if self.indention_mode is S.Indention_Mode.Tabulators:
			line = self.document[index]
			if (indent := line.indent) is not None:
				assert (level := indent.count('\t')) == len(indent)
				return level
		else:
			raise NotImplementedError()

	def get_min_indent(self):
		min_level = None

		for index, line in self.iter_lines(True):
			indent = self.compute_indent(index)
			if min_level is None or indent < min_level:
				min_level = indent
				if min_level == 0:
					break	#Early return

		return min_level


tr = Tree_Reference(Document(text))

for index, child in enumerate(tr.children):
	print(index, repr(child.title))
#print(repr(tr.title))

#root = Tree_Reference.from_str(text)



# for line in Document(text):
# 	print(line.first_non_indent_token, repr(line.indent), repr(line.body))
