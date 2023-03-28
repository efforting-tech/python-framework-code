from .. import rudimentary_type_system as RTS
from ..rudimentary_type_system.bases import standard_base
from .. import abstract_base_classes as ABC
from pathlib import Path

def left_shave(line, to_shave):
	if line.startswith(to_shave):
		return line[len(to_shave):]
	else:
		return line


def get_indention_prefix(line):
	stripped = line.lstrip('\t ')
	count = len(line) - len(stripped)
	prefix = line[:count]

	if prefix and prefix[0] in '\t ':
		assert not prefix.strip(prefix[0])

	return prefix

def get_indention_level(line, tab_size=4):
	prefix = get_indention_prefix(line)
	if prefix:
		if prefix[0] == '\t':
			return len(prefix) * tab_size

		elif prefix[0] == ' ':
			return len(prefix)

		else:
			raise Exception()

	return 0



def get_minimum_indention_level(lines, tab_size=4):
	minimum_indention = None
	for index, line in enumerate(lines):
		if line.strip():
			indention = get_indention_level(line, tab_size)
			if minimum_indention is None or indention < minimum_indention:
				minimum_indention = indention

	return minimum_indention or 0

def get_minimum_indention_prefix(lines):
	minimum_indention_prefix, minimum_indention_length = None, None
	for index, line in enumerate(lines):
		if line.strip():
			indention_prefix = get_indention_prefix(line)
			indention_length = len(indention_prefix)
			if minimum_indention_prefix is None or indention_length < minimum_indention_length:
				minimum_indention_prefix, minimum_indention_length = indention_prefix, indention_length

	return minimum_indention_prefix or ''



#Later we may have a text_node that operates on some source text, where you could manipulate a body of a body and have the changes reflected
#But for now we operate in a simpler manner, maybe the extended features should be a high level version of this

#We may also do away with the caching that takes mutability into account here for the low level type - condensing this a bit assuming we  always work with immutable data

@ABC.register_class_tree('text.node')
class text_node(standard_base):
	#TODO: __repr__ = field_based_representation('{self.title!r} {len(self.lines)} lines')
	#TODO: constructors

	#It would be nice with a liberal type that doesn't use any caching but instead allows mutating fields
	#or is we just solve the cache invalidation issue - two options.

	#RQ - methods accepting title should accept title being None

	lines = RTS.field(factory=tuple, read_only=True)

	@RTS.cached_property(lines)
	def title(self):
		if flc := self.first_line_with_contents:
			return flc.strip()

		#Note that the title is the first line no matter of its indention

	@RTS.cached_property(lines)
	def first_line_with_contents(self):
		flc = self.index_of_first_line_with_contents
		if flc is not None:
			return self.lines[flc]

	@RTS.cached_property(lines)
	def index_of_first_line_with_contents(self):
		return self.get_index_of_first_line_with_contents()

	@classmethod
	def from_text(cls, text):
		return cls(tuple(text.split('\n')))

	@classmethod
	def from_path(cls, path):
		return cls.from_text(Path(path).read_text())

	@classmethod
	def from_title_and_branches(cls, title, branches):
		lines = (title or '',)

		for b in branches:
			lines += b.indented_copy().lines

		return cls(lines)


	@classmethod
	def from_title_and_body(cls, title, body):
		if title is None:
			return cls(tuple(f'\t{l}' for l in body.lines))
		else:
			return cls((title, *(f'\t{l}' for l in body.lines)))


	def get_index_of_first_line_with_contents(self, start=0):
		for index, line in enumerate(self.lines[start:], start):
			if stripped := line.strip():
				return index




	def iter_nodes(self, include_blanks=False):
		minimum_indention = get_minimum_indention_level(self.lines)
		for index, line in enumerate(self.lines):
			if line.strip():
				indention = get_indention_level(line)
				if indention == minimum_indention:
					yield self.__class__(self.lines[index:])
			elif include_blanks:
				yield self.__class__()


	def get_body(self, include_blanks=True):
		flc = self.index_of_first_line_with_contents
		if flc is None:
			return self.__class__()

		if (slc := self.get_index_of_first_line_with_contents(flc+1)) is None:
			return text_node()


		flc_indention = get_indention_level(self.lines[flc])
		slc_indention = get_indention_level(self.lines[slc])

		#print(self, flc_indention, slc_indention)

		if slc_indention <= flc_indention:
			return self.__class__()

		for index, line in enumerate(self.lines[slc:], slc):
			if line.strip():
				indention = get_indention_level(line)

				if indention <= flc_indention:
					break

				last_index_with_content = index

			last_index = index

		if include_blanks:
			return self.__class__(self.lines[flc+1:last_index+1])
		else:
			return self.__class__(self.lines[slc:last_index_with_content+1])

	@RTS.cached_property(lines)
	def body(self):
		return self.get_body(False)

	@RTS.cached_property(lines)
	def has_contents(self):
		return bool(self.text.strip())

	@RTS.cached_property(lines)
	def text(self):
		#Assumes automatic dedention
		minimum_indention_prefix = get_minimum_indention_prefix(self.lines)
		skip = len(minimum_indention_prefix)
		return '\n'.join(line[skip:] if line.strip() else line for line in self.lines)

	def dedented_copy(self):
		prefix = get_minimum_indention_prefix(self.lines)
		return self.__class__(tuple(left_shave(l, prefix) for l in self.lines))

	def indented_copy(self, prefix='\t'):
		return self.__class__(tuple(f'{prefix}{l}' for l in self.lines))
