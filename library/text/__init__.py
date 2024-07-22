from ..document.structures import Hierarchial_Entry
from ..text.interface import Text_Interface
#TODO - these should not be in settings
from ..document.settings.indention import get_line_with_indent, format_line_with_indent
from ..record.base.public import Structure
from ..record import member as M
from .. import ABC

#TODO - move items to abstract types or specific interfaces as much as possible
COPY = object()




def calculate_indices_from_slice(s, fi, li):
	if s.start is None:
		start = fi
	elif s.start < 0:
		start = li + s.start
	else:
		start = fi + s.start

	if s.stop is None:
		stop = li
	elif s.stop < 0:
		stop = li + s.stop
	else:
		stop = fi + s.stop

	return start, stop

class Line(Hierarchial_Entry, ABC.Text.Line):
	indent = M.named(default=None)
	text = M.named(default=None)

	def copy(self, indent=COPY, text=COPY, parent=COPY):
		return type(self)(
			indent = self.indent if indent is COPY else indent,
			text = self.text if text is COPY else text,
			parent = self.parent if parent is COPY else parent,
		)

	@property
	def row(self):
		if parent := self.parent:
			return parent.get_row(self)

	@property
	def index(self):
		if parent := self.parent:
			return parent.index_of(self) + parent.first_index

	@classmethod
	def from_str(cls, source_line, **settings):
		new = cls(**settings)
		ds = new.document_settings
		new.text, new.indent = get_line_with_indent(source_line, ds)
		return new

	def to_str(self):
		return format_line_with_indent(self.text, self.indent, self.document_settings)

	def write(self, source_line):
		ds = self.document_settings
		assert ds.line_endings not in source_line
		if self.text is None:	#Note - we are assuming that indent is not defined if text is none. Maybe we should do this differently?
			self.text, self.indent = get_line_with_indent(source_line, ds)
		elif len(self.text) == 0:
			self.text, pending_indent = get_line_with_indent(source_line, ds)
			self.indent += pending_indent
		else:
			self.text += source_line

	@property
	def is_empty(self):
		return self.text is None or len(self.text) == 0

	def adjust_indention(self, adjustment):
		if adjustment == 0:
			return

		if self.indent is None:
			self.indent = 0

		self.indent = max(0, self.indent + adjustment)

	def clear_indention(self):
		self.indent = None


class Abstract_Line_Listing(Hierarchial_Entry, Text_Interface, ABC.Text.Block):
	def to_str(self):
		return self.document_settings.line_endings.join(l.to_str() for l in self.lines)


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

	def __len__(self):
		return len(self.lines)

	def casted_copy(self, new_type):
		#TODO - rewrite __getitem__ so that it uses a slicing method that can pass along view_type. This way we don't need to do the dirty __class__ hack
		copy = self[:]
		object.__setattr__(copy, '__class__', new_type)
		return copy


class Line_View(Abstract_Line_Listing):
	first_index = M.positional(default=None)
	last_index = M.positional(default=None)

	@property
	def first_row(self):
		return self.parent.first_row + self.first_index

	@property
	def lines(self):
		return self.parent.lines[self.first_index:self.last_index+1]

	def __getitem__(self, key_or_slice):
		match key_or_slice:
			case int():
				return self.lines[key_or_slice]

			case slice():
				return type(self).view_type(
					*calculate_indices_from_slice(key_or_slice, self.first_index, self.last_index),
					parent=self.parent,
				)

Line_View.view_type = Line_View

class Line_Listing(Abstract_Line_Listing):
	lines = M.named(factory=list)
	first_row = M.named(default=1)

	view_type = Line_View

	def __getitem__(self, key_or_slice):
		match key_or_slice:
			case int():
				return self.lines[key_or_slice]

			case slice():
				return type(self).view_type(
					*calculate_indices_from_slice(key_or_slice, self.first_index, self.last_index),
					parent=self,
				)


	@property
	def last_index(self):
		return len(self) - 1

	@property
	def first_index(self):
		return 0


	def clear(self):
		self.lines.clear()

	def adjust_indention(self, adjustment):
		if adjustment == 0:
			return

		for line in self.lines:
			line.adjust_indention(adjustment)

	def normalize_indention(self):
		self.adjust_indention(-self.get_minimum_indention())

	def strip_empty_lines(self):
		if (f := self.first_line_index_with_content) is None:
			self.clear()

		b = self.last_line_index_with_content
		self.lines = self.lines[f:b+1]

	def normalize_block(self):
		self.strip_empty_lines()
		self.normalize_indention()


	@property
	def last_line_index_with_content(self):
		for i, l in reversed(tuple(enumerate(self.lines))):
			if l.is_empty:
				continue

			return i

	def clear_indention(self):
		for line in self.lines:
			line.clear_indention()

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


	@classmethod
	def from_str(cls, source, **settings):
		new = cls(**settings)
		for source_line in source.split(new.document_settings.line_endings):
			new.lines.append(Line.from_str(source_line, parent=new))

		return new


	@property
	def has_trailing_newline(self):
		return self.lines and self.lines[-1].is_empty

	@property
	def is_starting_new_line(self):
		if self.lines:
			return self.lines[-1].is_empty
		else:
			return True

	@property
	def is_empty(self):
		return len(self.lines) == 0

	@property
	def last_line(self):
		if self.lines:
			return self.lines[-1]

	@property
	def first_line(self):
		if self.lines:
			return self.lines[0]


	def index_of(self, specific_line):
		return self.lines.index(specific_line)

	def get_row(self, specific_line):
		return self.lines.index(specific_line) + self.first_row


	def write(self, text):
		insert_newline = False
		for source_line in text.split(self.document_settings.line_endings):
			if insert_newline:
				self.lines.append(Line(parent=self))
			else:
				insert_newline = True

			if (last_line := self.last_line):
				last_line.write(source_line)
			else:
				self.lines.append(Line.from_str(source_line, parent=self))



