#TODO - provide local record/structure system
from efforting.mvp5.lazy_resources import acquire as acquire
TS, Public_Base = acquire('TS, TS_pb')

from .settings import Default_Document_Settings

class Hierarchial_Entry(Public_Base):
	parent = TS.named(default=None)

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

class Text_Match(Public_Base):
	source = TS.positional()
	token = TS.positional()
	match = TS.positional()
