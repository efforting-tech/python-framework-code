def debug_format_line_of_tokens(document, token_list, color_function=value_to_color_spiral):
	if not token_list:
		return ''

	result = ''
	previous_position = token_list[0].match.start()

	def value_to_color(value):
		num = (sum(map(ord, repr(freeze(value)))) / 29) % 1.0
		R, G, B = color_function(num)
		return f"\033[38;2;{R};{G};{B}m"

	for t in token_list:
		t_state = dict(t.__getstate__())
		match = t_state.pop('match')
		t_state['__class__'] = type(t)
		printable = match.group().replace('\n', '↵').replace(' ', '␣').replace('\t', '↹ ')

		if (head_length := match.start() - previous_position):
			inner = document.text[previous_position:match.start()]
			result += f'\033[7;39m{inner}\033[0m'


		result += f'{value_to_color(t_state)}{printable}'
		previous_position = match.end()


	result += '\033[0m'
	return result



def dump_node(node, indent=0):
	print(indent * '    ', debug_format_line_of_tokens(node.document, node.title_line.tokens))

	for index, child in enumerate(node.children):
		dump_node(child.body, indent+1)