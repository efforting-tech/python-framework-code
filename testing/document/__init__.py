from efforting.mvp6 import document
from efforting.mvp6.document.settings.indention import Indention_Mode

#TODO - use testing framework - be more comprehensive

doc = document.create_line_listing_document_from_str('''
\tHello World!
\t\tHow are you today?
''')

assert doc.lines[1].text == 'Hello World!'
assert doc.lines[2].text == 'How are you today?'
assert doc.lines[1].indent == 1
assert doc.lines[2].indent == 2

doc.document_settings.indention_mode = Indention_Mode.Spaces
assert doc.to_str() == '\n    Hello World!\n        How are you today?\n'

doc.document_settings.indention_string = '+'
doc.document_settings.indention_mode = Indention_Mode.CustomString
assert doc.to_str() == '\n+Hello World!\n++How are you today?\n'

def custom_indent(text, level):
	return f'[{level}] - {text!r}'

doc.document_settings.format_indent = custom_indent
doc.document_settings.indention_mode = Indention_Mode.CustomFunction

assert doc.to_str() == (
	"[0] - ''\n"
	"[1] - 'Hello World!'\n"
	"[2] - 'How are you today?'\n"
	"[0] - ''"
)