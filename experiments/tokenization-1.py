from tokenization_common import split_tokens_into_lines, value_to_color_spiral, freeze, tokens

#This is a good start - next session we should do the indention line thing (also see core.text)

state_set = set()

lines = tuple(split_tokens_into_lines(tokens, preserve_ends=True))
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
for (l, r) in lines:
	for t in tokens[l:r+1]:
		t_state = dict(t.__getstate__())
		match = t_state.pop('match')
		t_state['__class__'] = type(t)
		printable = match.group().replace('\n', '↵\n').replace(' ', '␣').replace('\t', '↹ ')

		result += f'{color[freeze(t_state)]}{printable}'

print(result, end='\033[0m')