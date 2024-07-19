#TODO - provide local record/structure system
from efforting.mvp5.lazy_resources import acquire as acquire
TS, Public_Base = acquire('TS, TS_pb')

from ..text import Line_Listing
from .settings import Document_Settings
from ..text.tree import Text_Tree

class Document(Public_Base):
	settings = TS.named(factory=Document_Settings)

	@property
	def document(self):
		return self


def create_line_listing_document_from_str(source, normalize_block=False, **document_settings):
	result = Line_Listing.from_str(source, parent=Document(**document_settings))
	#TODO - add more operations - or better yet- define a way to specify operations
	if normalize_block:
		result.normalize_block()
	return result

def create_text_tree_document_from_str(source, normalize_block=False, **document_settings):
	return Text_Tree.from_lines(create_line_listing_document_from_str(source, normalize_block, **document_settings))