from ..record.base.public import Structure
from ..record import member as M
from .settings import Default_Document_Settings

class Hierarchial_Entry(Structure):
	parent = M.named(default=None)

	@property
	def root(self):
		if self.parent:
			return self.parent.root
		else:
			return self

	@property
	def document(self):
		if self.parent:
			return self.parent.document

	@property
	def document_settings(self):
		if document := self.document:
			return self.document.settings
		else:
			return Default_Document_Settings

class Text_Match(Structure):
	source = M.positional()
	token = M.positional()
	match = M.positional()
