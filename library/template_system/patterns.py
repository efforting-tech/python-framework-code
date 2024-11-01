
def macro_pattern(pattern, input_str):
	return rf'§\s*{pattern(input_str)}'
