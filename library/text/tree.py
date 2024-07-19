#TODO - provide local record/structure system
from efforting.mvp5.lazy_resources import acquire as acquire
TS, Public_Base = acquire('TS, TS_pb')

from . import Line_View, Line_Listing

class Text_Tree(Line_View):
	@classmethod
	def from_lines(cls, lines):
		return lines.casted_copy(cls)

	@classmethod
	def from_str(cls, value):
		return Line_Listing.from_str(value).casted_copy(cls)

	@property
	def title(self):
		if flwc := self.first_line_with_content:
			return flwc.text

	@property
	def body(self):
		return self[1:]

	def iter_nodes(self):
		min_indent = min(i.indent for i in self.lines if i.text)
		last_root_index = None
		for local_index, i in enumerate(self):
			if not i.text:
				continue

			if i.indent == min_indent:
				if last_root_index is not None:
					yield self[last_root_index:local_index-1]

				last_root_index = local_index

		if last_root_index is not None:
			yield self[last_root_index:]

Text_Tree.view_type = Text_Tree


