from ...str.interface import String_Interface

class Text_Interface(String_Interface):
	def generic_text_operation(self, operation):
		self.lines = list(line.from_str(source_line, parent=self) for source_line in  operation(self.to_str()).split(self.document_settings.line_endings))

	def replace_contents_with_new_str(self, new_str):
		self.lines = list(line.from_str(source_line, parent=self) for source_line in new_str.split(self.document_settings.line_endings))

	def regex_replace(self, pattern, replace):
		self.replace_contents_with_new_str(re.compile(pattern).sub(replace, self.to_str()))



