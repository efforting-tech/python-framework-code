def terminal(input_str):
	words = input_str.split()
	return rf"{r'\s+'.join(words)}:?"

def path(input_str):
	words = input_str.split()
	return rf"{r'\s+'.join(words)}:?\s*([\w\.]+)"

def pattern(input_str):
	words = input_str.split()
	return rf"{r'\s+'.join(words)}:?\s*(.+)"

def non_spaces(required_count, optional_count=0, end_with_pattern=False):
	result = r''

	for i in range(required_count):
		if result:
			result += r'\s+'
		result += r'(\S+)'

	for i in range(optional_count):
		if result:
			result += r'(:?\s+(\S*))?'
		else:
			result += r'(\S*)'

	if end_with_pattern:
		if result:
			result += r'\s+'
		result += r'(.*)'

	return result


