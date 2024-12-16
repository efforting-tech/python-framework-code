from tokenization_common import split_tokens_into_lines, value_to_color_spiral, freeze, tokens, Indention
from efforting.tech.template1.core import records as R

import re

#In this experiment we will investigate how we can turn this into a tree
#We will also identify lines that represent statements - this will be different from our traditional regex based criteria since we must check the first token of the line


class line_ref(R.Record):
	tokens: R.Field()
	start: R.Field()
	end: R.Field()

	@property
	def first_token(self):
		if self.start > self.end:
			return

		return self.tokens[self.start]


	@property
	def first_non_indent_token(self):
		match self.first_token:
			case Indention(match=re.Match() as match) if self.start + 1 <= self.end:
				return self.tokens[self.start + 1]

			case non_indent:
				return non_indent

	@property
	def indent_match(self):
		match self.first_token:
			case Indention(match=re.Match() as match):
				return match

#TODO - this should be some sort of document referencing lines and tokens
lines = tuple(split_tokens_into_lines(tokens, preserve_ends=True))


state_set = set()
for (l, r) in lines:
	for t in tokens[l:r+1]:
		t_state = dict(t.__getstate__())
		match = t_state.pop('match')
		t_state['__class__'] = type(t)
		state_set.add(freeze(t_state))

color = dict()
for i, s in enumerate(sorted(state_set, key=repr)):
	R, G, B = value_to_color_spiral(i / len(state_set))
	color[s] = f"\033[38;2;{R};{G};{B}m"



del state_set

result = ''
for line_no, (l, r) in enumerate(lines, 1):


	lref = line_ref(tokens, l, r)

	result += f'First: {lref.first_non_indent_token!r}\n'
	result += f'{line_no:03}: '
	for t in tokens[l:r+1]:
		t_state = dict(t.__getstate__())
		match = t_state.pop('match')
		t_state['__class__'] = type(t)
		printable = match.group().replace('\n', '↵\n').replace(' ', '␣').replace('\t', '↹ ')

		result += f'{color[freeze(t_state)]}{printable}'

	result += '\033[0m\n'

print(result)
