from .. import Line_View, Line_Listing
from ... import symbol

class Text_Tree_Interface:
	#TODO - make sure this is correct - we moved it from specific class to interface
#	@classmethod
#	def from_lines(cls, lines):
#		return lines.casted_copy(cls)

	@classmethod
	def from_title_and_branches(cls, title, *branches):
		new = cls()
		new.write(title)
		for b in branches:
			new.write(b, 1)
		return new


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
		min_indent = min(i.indent for i in self.lines if i.text)		#BUG fails if iterator is empty: ValueError: min() iterable argument is empty
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



class Abstract_Text_Tree(Text_Tree_Interface):
	pass

class Text_Tree_View(Abstract_Text_Tree, Line_View):
	pass

class Text_Tree_Listing(Abstract_Text_Tree, Line_Listing):
	def write(self, source_item, adjust_indent=None):
		if isinstance(source_item, Text_Tree_Interface):	#TODO  use ABC
			for l in source_item.lines:
				if adjust_indent is None:
					new_indent = symbol.copy
				else:
					new_indent = max(0, l.indent + adjust_indent)

				self.lines.append(l.copy(parent=self, indent=new_indent))

		else:
			super().write(source_item)

Abstract_Text_Tree.editable_type = Text_Tree_Listing
Abstract_Text_Tree.view_type = Text_Tree_View

