import unicodedata, re
from ...document.settings import Default_Document_Settings
from ...document.settings.indention import format_line_with_indent
from ...text.styling import Stylized_Span, HSV, RGB, apply_style_operations
from ...text.styling import presets
from ...text.formatting.ansi import styles

def stylize_row_number(row, digits=3):
	text = str(row)
	leading_zeros = '0' * (digits - len(text))
	result = Stylized_Span()
	result.write_stylized('row-leading-zeros', leading_zeros)
	result.write_stylized('row-value', text)
	return result


def format_tab(length):
	if length == 1:
		return '🬃'
	else:
		return f'🬇{"🬋"*(length-2)}🬃'

def stylize_text(text, first_row=1, settings=Default_Document_Settings, highlight_spans=()):
	result = Stylized_Span()

	def check_spans(character_pos, text):
		def write_stylized(style, text):
			result.write_stylized(style, text)

		for span in highlight_spans:
			match span:
				case re.Match():
					lb, hb = span.span()
					if lb <= character_pos < hb:
						def write_stylized(style, text):
							result.write_stylized(style, Stylized_Span('highlight', text))
						break

				case (re.Match() as span, str() as span_style):
					lb, hb = span.span()
					if lb <= character_pos < hb:
						def write_stylized(style, text):
							result.write_stylized(style, Stylized_Span(span_style, text))
						break

				case otherwise:
					raise Exception(span)

		return write_stylized


	lines = text.split(settings.line_endings)
	character_pos = 0
	for index, line in enumerate(lines):
		row = index + first_row

		result.write(stylize_row_number(row))
		result.write(' ')

		line_length = 0
		for c in line:
			write_stylized = check_spans(character_pos, text)
			character_pos += 1

			if c == ' ':
				write_stylized('white-space', '·')
				line_length += 1

			elif c == '\t':
				remaining = settings.indention_width - (line_length % settings.indention_width)
				write_stylized('white-space', format_tab(remaining))
				line_length += remaining

			elif (uc := unicodedata.category(c)) and uc == 'Cc':
				write_stylized('control-character', c)

			else:
				write_stylized('text', c)

		write_stylized = check_spans(character_pos, text)

		if index < len(lines) - 1:
			write_stylized('white-space', '↵')
		else:
			if line_length == 0:	#Skip printing last line if it is empty
				break

		if index < len(lines) - 1:
			result.write('\n')
			character_pos += len(settings.line_endings)

	return result

def render_ansi_control_sequences(span_list, ansi_style=styles.default):
	result = ''
	for ss in span_list:
		enter_span_list = list()
		exit_span_list = list()

		fgc, bgc = ss.state['foreground_color'], ss.state['background_color']

		match fgc:
			case HSV():
				fg_enter_span = ';'.join(('38', '2', *map(str, fgc.to_rgb().to_integers(8))))
				fg_exit_span = '39'

			case str():
				fg_enter_span, fg_exit_span = ansi_style.fgc_lut.get(fgc, (None, None))

			case null if null is None:
				fg_enter_span, fg_exit_span = None, None

			case otherwise:
				raise Exception(fgc)

		match bgc:
			case HSV():
				inner =  ';'.join(('48', '2', *map(str, fgc.to_rgb().to_integers(8))))
				fg_enter_span = f''
				fg_exit_span = '49'

			case str():
				bg_enter_span, bg_exit_span = ansi_style.bgc_lut.get(bgc, (None, None))

			case null if null is None:
				bg_enter_span, bg_exit_span = None, None

			case otherwise:
				raise Exception(bgc)



		if fg_enter_span:
			enter_span_list.append(fg_enter_span)

		if bg_enter_span:
			enter_span_list.append(bg_enter_span)

		if fg_exit_span:
			exit_span_list.append(fg_exit_span)

		if bg_exit_span:
			exit_span_list.append(bg_exit_span)

		for flag, (flag_enter_span, flag_exit_span) in ansi_style.flag_lut.items():
			#TODO - should we have ways to warn/error for missing states?
			if ss.state.get(flag, False):
				enter_span_list.append(flag_enter_span)
				exit_span_list.append(flag_exit_span)

		#TODO - should we have ways to warn/error for flags not present in the styles?

		if enter_span_list:
			result += f'\x1b[{";".join(enter_span_list)}m'

		text = ss.text
		for text_filter in ss.state['filters']:
			text = text_filter(text)

		result += text

		if exit_span_list:
			result += f'\x1b[{";".join(exit_span_list)}m'

	return result

def stylize_and_render_document(document, style=presets.default, highlight_spans=()):
	return render_ansi_control_sequences(apply_style_operations(stylize_text(document.to_str(), document.first_row, document.document_settings, highlight_spans=highlight_spans), style))
