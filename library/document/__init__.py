from ..record.base.public import Structure
from ..record import member as M
from .structures import Document

from pathlib import Path

def create_line_listing_document_from_str(source, normalize_block=False, **document_settings):
	from ..text import Line_Listing
	result = Line_Listing.from_str(source, parent=Document(**document_settings))
	#TODO - add more operations - or better yet- define a way to specify operations
	if normalize_block:
		result.normalize_block()
	return result

def create_text_tree_document_from_str(source, normalize_block=False, **document_settings):
	from ..text.tree import Text_Tree_Listing
	return Text_Tree_Listing.from_lines(create_line_listing_document_from_str(source, normalize_block, **document_settings))

def create_line_listing_document_from_path(source, normalize_block=False, **document_settings):
	return create_line_listing_document_from_str(Path(source).read_text(), normalize_block=normalize_block, **document_settings)

def create_text_tree_document_from_path(source, normalize_block=False, **document_settings):
	return create_text_tree_document_from_str(Path(source).read_text(), normalize_block=normalize_block, **document_settings)
