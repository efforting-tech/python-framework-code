from .indention import Indention_Mode
from ...record.base.public import Structure
from ...record import member as M

@lambda x:x()	#TODO use a named function
class Default_Document_Settings(Structure):
	indention_mode = M.constant(Indention_Mode.Tabs)
	indention_width = M.constant(4)
	line_endings = M.constant('\n')
	indention_string = M.constant(None)
	format_indent = M.constant(None)
	parse_indent = M.constant(None)

class Document_Settings(Structure):
	indention_mode = M.named(default=Default_Document_Settings.indention_mode)
	indention_width = M.named(default=Default_Document_Settings.indention_width)
	line_endings = M.named(default=Default_Document_Settings.line_endings)
	indention_string = M.named(default=Default_Document_Settings.indention_string)
	format_indent = M.named(default=Default_Document_Settings.format_indent)
	parse_indent = M.named(default=Default_Document_Settings.parse_indent)

	def update(self, **settings):
		for key, value in settings.items():
			#TODO - support deletion
			#TODO - verify setting exists
			setattr(self, key, value)
