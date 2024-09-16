from ..text import Immutable_Line_View_Interface, Mutable_Line_View_Interface

class Core_Text_Tree_Interface:
	@property
	def title(self):
		if flwc := self.first_line_with_content:
			return flwc.text

	@property
	def body(self):
		first = None
		first_indent = None
		last = None
		for i, l in enumerate(self.lines):
			if l.is_empty:
				continue

			if first is None:
				first = i
				first_indent = l.indent
			else:
				if l.indent > first_indent:
					last = i

		#LIKELY BUG when dealing with empty bodies
		return self[first+1:last]


	def iter_nodes(self):
		min_indent = min(i.indent for i in self.lines if i.text)		#BUG fails if iterator is empty: ValueError: min() iterable argument is empty
		last_root_index = None
		for local_index, i in enumerate(self):
			if not i.text:
				continue

			if i.indent < min_indent:
				break

			elif i.indent == min_indent:
				if last_root_index is not None:
					yield self[last_root_index:local_index-1]

				last_root_index = local_index

		if last_root_index is not None:
			yield self[last_root_index:]


class Immutable_Text_Tree_Interface(Core_Text_Tree_Interface, Immutable_Line_View_Interface):
	pass

class Mutable_Text_Tree_Interface(Core_Text_Tree_Interface, Mutable_Line_View_Interface):
	pass
