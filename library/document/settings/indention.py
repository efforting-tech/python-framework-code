#TODO - provide local symbol implementation
from efforting.mvp4.symbols import symbol as Symbol


#TODO - this should be enum-ish
class Indention_Mode:
	IM = Symbol('Indention_Mode')
	Tabs = IM()
	Spaces = IM()
	CustomString = IM()
	CustomFunction = IM()

#TODO - move out of here
def format_line_with_indent(text, indent, settings):
	if text is None:
		text = ''

	if indent is None:
		return text
	else:
		indention_mode = settings.indention_mode
		if indention_mode is Indention_Mode.Tabs:
			return '\t' * indent + text
		elif indention_mode is Indention_Mode.Spaces:
			return ' ' * indent * settings.indention_width + text
		elif indention_mode is Indention_Mode.CustomString:
			assert settings.indention_string is not None
			return settings.indention_string * indent + text
		elif indention_mode is Indention_Mode.CustomFunction:
			assert (format_indent := settings.format_indent)
			return format_indent(text, indent)
		else:
			raise Exception()

def get_line_with_indent(source_line, settings):
	indention_mode = settings.indention_mode

	if indention_mode is Indention_Mode.Tabs:
		text = source_line.lstrip('\t')
		indent = len(source_line) - len(text)
		return text, indent

	elif indention_mode is Indention_Mode.Spaces:
		#TODO - reuse code for customstring and spaces
		assert (indention_string := settings.indention_width * ' ')
		indent = 0

		while True:
			head, sep, tail = source_line.partition(indention_string)

			if head:
				break
			elif sep:
				indent += 1
				source_line = tail
			else:
				break

		return source_line, indent

	elif indention_mode is Indention_Mode.CustomString:
		assert (indention_string := settings.indention_string)
		indent = 0

		while True:
			head, sep, tail = source_line.partition(indention_string)

			if head:
				break
			elif sep:
				indent += 1
				source_line = tail
			else:
				break

		return source_line, indent

	else:
		raise Exception()

