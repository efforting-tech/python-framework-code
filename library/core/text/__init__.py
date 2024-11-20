from .. import typing as TY
from .. import record as R
from ... import ABC, Symbol

#TODO - move to core string utils
def expand_tabs_in_line(line, tab_width=4):
	result = ''
	for c in line:
		if c == '\t':
			result += ' ' * (tab_width - len(result) % tab_width)
		else:
			result += c

	return result

def expand_tabs(text, tab_width=4):
	return '\n'.join(expand_tabs_in_line(l, tab_width) for l in text.split('\n'))



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

	def copy(self, adjust_indent=0, indention=Symbol.Default):
		#TODO - maybe we should have a feature for dealing with settings to make these thigns easier to chain

		if indention is Symbol.Default:
			effective_indention = '\t'
		else:
			effective_indention = indention

		if adjust_indent or indention is not Symbol.Default:
			adjusted_indent = max(self.indent + adjust_indent, 0)
			return type(self)(adjusted_indent * effective_indention + self.value)
		else:
			return type(self)(self.text)



@ABC.Text.Line.Immutable
class Immutable_Line(Core_Line):
	text: 			R.Field_Update(type=ABC.String, mutable=False)

	@classmethod
	def from_anything(cls, value):
		match value:
			case cls():
				return value	#Immutable can share
			case str():
				return cls(value)
			case unmatched:
				raise TypeError(type(value))

@ABC.Text.Line.Mutable
class Mutable_Line(Core_Line):
	text: 			R.Field_Update(type=ABC.String, mutable=True)	#BUG - Why do we have to specify true here when Core_Line is mutable?


	@classmethod
	def from_anything(cls, value):
		match value:
			case str():
				return cls(value)
			case unmatched:
				raise TypeError(type(value))




@ABC.Text.Line_View
class Core_Line_View(R.Record):
	lines:			R.Field(type=TY.Sequence(ABC.Text.Line))

	def convert_tabs_to_spaces(self, spaces=4):
		#TODO - the class should define a line type that is then used in the Field declaration
		#		but this requires the resolution system to get a suitable concrete type from the ABC
		#return type(self)(type(self.lines)(LT(expand_tabs_in_line(line.text, spaces)) for line in self.lines))

		return type(self)('\n'.join(expand_tabs_in_line(line.text, spaces) for line in self.lines))

	def get_min_indent(self):
		return min((i.indent for i in self.lines if i.value), default=None)

	def to_str(self, indention=Symbol.Default):
		#TODO - should we have a type further down the type chain for custom newlines?
		return '\n'.join(l.to_str(indention=indention) for l in self.lines)

	@property
	def is_empty(self):
		return len(self.to_str()) == 0


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

	@property
	def last_line_index_with_content(self):
		for i, l in reversed(tuple(enumerate(self.lines))):
			if l.is_empty:
				continue

			return i

	@property
	def last_line_with_content(self):
		for l in reversed(self.lines):
			if l.is_empty:
				continue

			return l

	def copy(self, adjust_indent=0, indention=Symbol.Default):
		return type(self)([l.copy(adjust_indent=adjust_indent, indention=indention) for l in self])

	def normal(self, extra_adjustment=0):
		if (fliwc := self.first_line_index_with_content) is None:
			return type(self)()	#Create empty

		lliwc = self.last_line_index_with_content

		c = self[fliwc:lliwc+1]
		return c.copy(adjust_indent=extra_adjustment-(c.get_min_indent() or 0))

	def normal_str(self, indention=Symbol.Default):	#Shorthand
		return self.normal().to_str(indention=indention)


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

	@classmethod
	def from_str(cls, value):	#NOTE - we must use different one for mutable sub classes
		return cls(tuple(map(Immutable_Line.from_anything, value.splitlines())))

	def __init__(self, text=None):
		#NOTE - we can't use match here because ABC nodes are not actually types

		if text is None:
			lines = ()
		elif isinstance(text, ABC.String):
			lines = tuple(map(Immutable_Line, text.splitlines()))
		elif isinstance(text, ABC.Sequence):
			#TODO - now we are just assuming this is a sequence of lines but we should really use the conversion system to make this flexible
			assert isinstance(text, (tuple, list))
			lines = tuple(text)
		else:
			raise TypeError(text)

		super().__init__(lines)


@ABC.Text.Line_View.Mutable
class Mutable_Line_View(Core_Line_View):
	lines:			R.Field_Update(type=TY.Sequence(ABC.Text.Line.Mutable), mutable=True)


	@classmethod
	def from_str(cls, value):
		return cls(list(map(Mutable_Line.from_anything, value.splitlines())))




	def write_line(self, line='', indent_adjustment=0):
		self.lines.append(Mutable_Line(line).copy(adjust_indent=indent_adjustment))

	def write_pieces(self, piece_list, indent_adjustment=0):
		if not piece_list:
			return

		for piece in piece_list:
			self.write(piece, indent_adjustment=indent_adjustment)


	def write(self, piece, indent_adjustment=0):
		if not piece:
			return

		if isinstance(piece, ABC.Text.Block):
			for line in piece:
				self.lines.append(Mutable_Line(line.copy(adjust_indent=indent_adjustment).text))	#NOTE - we only need to copy if we have non zero indent_adjustment, it may be better to have a feature in the constructor
		elif isinstance(piece, ABC.Text.Line):
			self.lines.append(Mutable_Line(piece.copy(adjust_indent=indent_adjustment).text))	#NOTE - we only need to copy if we have non zero indent_adjustment, it may be better to have a feature in the constructor

		else:
			raise TypeError(piece)


		#TODO - convert to match once we fix our ABC system
		# match piece:

		# 	case ABC.Text.Block(lines=lines):
		# 		print(lines)

		# 	case unhandled:
		# 		raise TypeError(piece)

	def insert(self, index, line):
		#TODO - some more convenient converter?
		if isinstance(line, ABC.Text.Line.Mutable):
			pass	#Already what we want

		elif isinstance(line, ABC.Text.Line):
			line = Mutable_Line(line.text)

		elif isinstance(line, ABC.String):
			line = Mutable_Line(line)

		else:
			raise TypeError(line)

		self.lines.insert(index, line)

	def __init__(self, text=None):
		#NOTE - we can't use match here because ABC nodes are not actually types


		if text is None:
			lines = list()
		elif isinstance(text, ABC.String):
			lines = list(map(Mutable_Line, text.splitlines()))
		elif isinstance(text, ABC.Sequence):
			#TODO - now we are just assuming this is a sequence of lines but we should really use the conversion system to make this flexible
			assert isinstance(text, (tuple, list))
			lines = list(text)
		else:
			raise TypeError(text)

		super().__init__(lines)



@ABC.Text.Tree_View
class Core_Tree_View(Core_Line_View):

	#TODO - adapt and implement this interface

	# @classmethod
	# def from_title_and_body(cls, title, body, clean_body=False):
	# 	new = cls()
	# 	new.write(title)
	# 	adjustment = 1
	# 	if clean_body:
	# 		adjustment -= body.get_minimum_indention()
	# 	new.write(body, adjustment)

	# 	return new

	# @classmethod
	# def from_title_and_branches(cls, title, *branches):
	# 	new = cls()
	# 	new.write(title)
	# 	for b in branches:
	# 		new.write(b, 1)
	# 	return new

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
		min_indent = self.get_min_indent()
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



@ABC.Text.Block.Immutable
@ABC.Text.Tree.Immutable
class Immutable_Tree_View(Core_Tree_View, Immutable_Line_View):
	@classmethod
	def from_anything(cls, value):
		match value:
			case cls():
				return value	#It is immutable so is fine to share
			case str():
				return cls.from_str(value)
			case unmatched:
				raise TypeError(type(value))



@ABC.Text.Block.Mutable
@ABC.Text.Tree.Mutable
class Mutable_Tree_View(Core_Tree_View, Mutable_Line_View):
	pass


	#TODO - adapt and implement this interface
	# def write(self, source_item, adjust_indent=None):
	# 	if isinstance(source_item, Text_Tree_Interface):	#TODO  use ABC
	# 		for l in source_item.lines:
	# 			if adjust_indent is None:
	# 				new_indent = symbol.copy
	# 			else:
	# 				new_indent = max(0, l.indent + adjust_indent)

	# 			self.lines.append(l.copy(parent=self, indent=new_indent))

	# 	else:
	# 		super().write(source_item)