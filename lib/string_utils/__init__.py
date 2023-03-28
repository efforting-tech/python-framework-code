#TODO - harmonize stuff from /home/devilholk/Projects/efforting-mvp-2/library/string_utils.py
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

def expand_tabs_and_return_lines(text, tab_width=4):
	return tuple(expand_tabs_in_line(l, tab_width) for l in text.split('\n'))

def expand_tabs_and_return_line_iterator(text, tab_width=4):
	return (expand_tabs_in_line(l, tab_width) for l in text.split('\n'))

def remove_blank_lines(line_generator):
	for l in line_generator:
		if l.strip():
			yield l


def str_check_prefix(to_check, prefix, silent=False):
	if silent and not isinstance(to_check, str):
		return

	if to_check.startswith(prefix):
		return to_check[len(prefix):]
