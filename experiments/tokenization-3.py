from tokenization_common import split_tokens_into_lines, value_to_color_spiral, freeze, Indention, template_tokenizer, NEW_LINE, Token
from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import ABC, Symbol as S

import re

#In this experiment we will investigate how we can turn this into a tree
#We will also identify lines that represent statements - this will be different from our traditional regex based criteria since we must check the first token of the line

# text = '''

# 	Hello World! Here is the <<== inline expression ==>>!
# 	This is a <<==! literal thing
# \t
# 	##==! Not a statement

# 	##== IS as a statement
# 		with a body too

# <<==HELLO==>>'''



#Experiment

text = '''<<==HELLO==>> TAIL
HEAD <<==HELLO <<==!NESTED HELLO!==>> ==>>
##== Statement
	with body
FINAL <<==HELLO==>>'''



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

	@property
	def line_count(self):
		return self.last_line - self.first_line + 1

	def _init_last_line(self):
		return len(self.document) - 1

	def _init_children(self):
		base_indent = self.base_indent

		result = list()
		last_index = self.first_line

		def add_chunk(index, is_last=False):
			nonlocal last_index
			if is_last and (last_index, index) == (self.first_line, self.last_line):
				return

			if is_last and last_index > index - 1:
				result.append(Tree_Reference(self.document, last_index, index))
			else:
				if index > 0:
					result.append(Tree_Reference(self.document, last_index, index-1))
			last_index = index

		for index, line in self.iter_lines(True):
			indent = self.compute_indent(index)
			if indent == base_indent:
				add_chunk(index)

		add_chunk(self.last_line, True)
		return tuple(result)


	def iter_lines(self, only_with_content=False):
		for index in range(self.first_line, self.last_line + 1):
			line = self.document[index]
			if only_with_content and not line.body_span:
				continue
			yield (index, line)

	@property
	def title(self):
		if body_text := self.document[self.first_line].body_text:
			return body_text.strip()

	@property
	def text(self):
		return '\n'.join(l.text for i, l in self.iter_lines())

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
	print(index, child.first_line, child.last_line, repr(child.title))
	for index, line in child.iter_lines():
		print('   ', repr(line.text))

#OUTPUT 1

# 0 0 -1
# 1 0 0
#     'HELLO==>> TAIL\n'
# 2 1 1
#     'HEAD <<==HELLO==>>\n'
# 3 2 2
#     'FINAL <<==HELLO'



def format_tree_and_color_by_token(tree, color_function=value_to_color_spiral):
	state_set = set()
	previous_position = 0
	for index, line in tree.iter_lines():
		l, r = line.start, line.end
		for t in tree.document.tokens[l:r+1]:
			t_state = dict(t.__getstate__())
			match = t_state.pop('match')
			t_state['__class__'] = type(t)

			#if (head_length := match.start() - previous_position):
			#	state_set.add(None)

			state_set.add(freeze(t_state))
			previous_position = match.end()


	color = dict()
	for i, s in enumerate(sorted(state_set, key=repr)):
		R, G, B = color_function(i / len(state_set))
		color[s] = f"\033[38;2;{R};{G};{B}m"

	result = ''
	previous_position = 0
	for index, line in tree.iter_lines():
		l, r = line.start, line.end

		for t in tree.document.tokens[l:r+1]:
			t_state = dict(t.__getstate__())
			match = t_state.pop('match')
			t_state['__class__'] = type(t)
			printable = match.group().replace('\n', '↵\n').replace(' ', '␣').replace('\t', '↹ ')

			if (head_length := match.start() - previous_position):
				#state_set.add(None)
				inner = tree.document.text[previous_position:match.start()]
				#result += f'{color[None]}{inner}'
				result += f'\033[7;39m{inner}\033[0m'



			result += f'{color[freeze(t_state)]}{printable}'
			previous_position = match.end()

	tail = tree.document.text[previous_position:]
	if tail:
		#result += f'{color[None]}{tail}'
		result += f'\033[7;39m{tail}\033[0m'


	result += '\033[0m'
	return result, color

result, colors = format_tree_and_color_by_token(tr)
import textwrap

print('\033[1;4mResult\033[0m')
print(textwrap.indent(result, '    '))
print()
print('\033[1;4mLegend\033[0m')
for key, col in sorted(colors.items(), key=repr):
	d = dict(key)
	c = d.pop('__class__')
	di = ' '.join(f'{k}={v!r}' for k,v in d.items())
	print(f'    {col}\033[3m{c.__qualname__}({di})\033[0m')

#OUTPUT 2 (nicely colored)

# <<==HELLO==>>␣TAIL↵
# HEAD␣<<==HELLO==>>↵
# FINAL␣<<==HELLO==>>

