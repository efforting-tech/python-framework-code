from .. import typing as TY
from .. import record as R
from ... import ABC, Symbol


@ABC.Text.Line
class Core_Line(R.Record):
	text: 			R.Field(type=ABC.String)

	@property
	def indent(self):
		return len(self.text) - len(self.text.lstrip('\t'))

	@property
	def value(self):
		return self.text.lstrip('\t')

	@property
	def is_empty(self):
		return not bool(self.text.lstrip('\t'))

	def to_str(self, indention=Symbol.Default):
		#TODO - we could later have more capable indention features
		if indention is not Symbol.Default:
			return self.indent * indention + self.value

		return self.text


@ABC.Text.Line.Immutable
class Immutable_Line(Core_Line):
	text: 			R.Field_Update(type=ABC.String, mutable=False)



@ABC.Text.Line_View
class Core_Line_View(R.Record):
	lines:			R.Field(type=TY.Sequence(ABC.Text.Line))


	def to_str(self, indention=Symbol.Default):
		#TODO - should we have a type further down the type chain for custom newlines?
		return '\n'.join(l.to_str(indention=indention) for l in self.lines)

	@property
	def first_line_index_with_content(self):
		for i, l in enumerate(self.lines):
			if l.is_empty:
				continue

			return i

	@property
	def first_line_with_content(self):
		for l in self.lines:
			if l.is_empty:
				continue

			return l

	def get_minimum_indention(self):
		mi = None

		for l in self.lines:
			if l.is_empty:
				continue

			if (indent := l.indent) is None:
				indent = 0

			if indent == 0:
				return 0

			if mi is None:
				mi = indent
			elif indent < mi:
				mi = indent

		return mi or 0

	def __len__(self):
		return len(self.lines)

	def __iter__(self):
		yield from self.lines

	def __getitem__(self, index_or_slice):
		if isinstance(index_or_slice, slice):
			return type(self)(self.lines[index_or_slice])

		return self.lines[index_or_slice]

@ABC.Text.Line_View.Immutable
class Immutable_Line_View(Core_Line_View):
	lines:			R.Field_Update(type=TY.Sequence(ABC.Text.Line.Immutable), mutable=False)

	def __init__(self, text):
		#NOTE - we can't use match here because ABC nodes are not actually types

		if isinstance(text, ABC.String):
			lines = tuple(map(Immutable_Line, text.splitlines()))
		elif isinstance(text, ABC.Sequence):
			#TODO - now we are just assuming this is a sequence of lines but we should really use the conversion system to make this flexible
			assert isinstance(text, tuple)
			lines = text
		elif text is None:
			lines = ()
		else:
			raise TypeError(text)

		super().__init__(lines)


@ABC.Text.Tree_View
class Core_Tree_View(Core_Line_View):

	@property
	def title(self):
		if flwc := self.first_line_with_content:
			return flwc.value.strip() or None

	@property
	def body(self):
		first = None
		first_indent = None
		last = None
		for i, l in enumerate(self.lines):
			if l.is_empty:
				continue

			if first is None:
				first = i + 1
				first_indent = l.indent
			else:
				last = i + 1

				#if l.indent > first_indent:
				if l.indent <= first_indent:
					break

		return self[first:last]


	def iter_nodes(self):
		min_indent = min((i.indent for i in self.lines if i.value), default=None)
		if min_indent is None:
			return

		last_root_index = None
		for local_index, i in enumerate(self):
			if not i.value:
				continue

			if i.indent < min_indent:
				break

			elif i.indent == min_indent:
				if last_root_index is not None:
					yield self[last_root_index:local_index]

				last_root_index = local_index

		if last_root_index is not None:
			yield self[last_root_index:]

class Immutable_Tree_View(Core_Tree_View, Immutable_Line_View):
	pass