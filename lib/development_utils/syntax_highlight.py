from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter, HtmlFormatter
from pygments.lexers import get_all_lexers, get_lexer_by_name
from pygments.styles import get_style_by_name
from fnmatch import fnmatch
import pathlib

extension_lexer_map = {pattern: name for name, aliases, filetypes, mimetypes in get_all_lexers() for pattern in filetypes}

style = get_style_by_name('fruity')
ANSI_formatter = TerminalTrueColorFormatter, dict(linenos=True, style=style, bg='dark')

def get_lexer_for_path(path):
	if isinstance(path, str):
		path = pathlib.Path(path)

	if path.is_symlink():
		match_path = path.readlink()
	else:
		match_path = path

	for ext, name in extension_lexer_map.items():
		if fnmatch(match_path, ext):
			try:
				return get_lexer_by_name(name, tabsize=4)
			except Exception as e:
				print('wtf?', e)
				return

def can_highlight(path):
	if isinstance(path, str):
		path = pathlib.Path(path)
	return get_lexer_for_path(path) is not None

def get_highlighted_terminal(path):
	lexer = get_lexer_for_path(path)
	formatter, formatter_settings = ANSI_formatter
	return highlight(path.read_text(), lexer, formatter(**formatter_settings))

def get_highlighted_terminal_from_text(text, language='python3'):
	lexer = get_lexer_by_name(language)
	formatter, formatter_settings = ANSI_formatter
	return highlight(text, lexer, formatter(**formatter_settings))


def print_code(code, lexer='python3', start_line=1):
	formatter, formatter_settings = ANSI_formatter
	fmt = formatter(**formatter_settings)
	fmt._lineno = start_line - 1 	#Ugly hack because some formatters in pygments doesn't allow to specify first line number in the constructor.
	print(highlight(code, get_lexer_by_name(lexer, tabsize=4), fmt))