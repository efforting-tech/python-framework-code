from efforting.mvp4.development_utils.syntax_highlight import get_highlighted_terminal_from_text as inner_get_highlighted_terminal_from_text, ANSI_formatter

#In this test we don't want linenos
#TODO - this should use the configuration system we figured out
ANSI_formatter[1]['linenos'] = False


def strip_rl_wrap(t):
	in_band = True
	result = ''
	for c in t:
		if in_band and c == '\001':
			in_band = False
		elif not in_band and c == '\002':
			in_band = True
		elif in_band:
			result += c

	return result

def count_empty_head_lines(lines):
	count = 0
	for line in lines:
		if not strip_rl_wrap(line).strip():
			count += 1
		else:
			break

	return count

def count_empty_tail_lines(lines):
	return count_empty_head_lines(reversed(lines))


def get_highlighted_terminal_from_lines(lines):
	offset = count_empty_head_lines(lines)
	#Add a trailing empty line that we then can unconditionally trim - ideally we'd use a highlighter that preserves the lines.
	#TODO - write our own ansi formatter (we should consider the AST based one that also can adjust the hue of items based on nesting level and such to improve readability)
	#It would also be good to store the lines with their indention so that we can change idention easy, maybe we should simply use the text_tree type together with line numbers
	lines = lines[offset:-count_empty_tail_lines(lines) or None] + ['']
	result = inner_get_highlighted_terminal_from_text('\n'.join(lines)).split('\n')

	source_head = count_empty_head_lines(lines)
	result_head = count_empty_head_lines(result)

	if source_head > result_head:
		result = ['' for i in range(source_head - result_head)] + result
	elif source_head < result_head:
		raise Exception('Not implemented')



	result = result[:-count_empty_tail_lines(result)]


	# for i in lines:
	# 	print('L', i)

	# for i in result:
	# 	print('R', i)

	assert len(result) + 1 == len(lines)

	return ['']*offset + result