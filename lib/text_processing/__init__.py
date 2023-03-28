def expand_tabs_in_line(line, tab_width=4):
	result = ''
	for c in line:
		if c == '\t':
			result += ' ' * (tab_width - len(result) % tab_width)
		else:
			result += c

	return result

def expand_tabs(text, tab_width=4):
	return '\n'.join(expand_tabs_in_line(l, tab_width) for l in text.split('\n'))
