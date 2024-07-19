from .indention import Indention_Mode

#TODO - provide local record/structure system
from efforting.mvp5.lazy_resources import acquire as acquire
TS, Public_Base = acquire('TS, TS_pb')


@lambda x:x()	#TODO use a named function
class Default_Document_Settings:
	indention_mode = TS.constant(Indention_Mode.Tabs)
	indention_width = TS.constant(4)
	line_endings = TS.constant('\n')
	indention_string = TS.constant(None)
	format_indent = TS.constant(None)
	parse_indent = TS.constant(None)

class Document_Settings(Public_Base):
	indention_mode = TS.named(default=Default_Document_Settings.indention_mode)
	indention_width = TS.named(default=Default_Document_Settings.indention_width)
	line_endings = TS.named(default=Default_Document_Settings.line_endings)
	indention_string = TS.named(default=Default_Document_Settings.indention_string)
	format_indent = TS.named(default=Default_Document_Settings.format_indent)
	parse_indent = TS.named(default=Default_Document_Settings.parse_indent)

	def update(self, **settings):
		for key, value in settings.items():
			#TODO - support deletion
			#TODO - verify setting exists
			setattr(self, key, value)
