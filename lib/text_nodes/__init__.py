from .. import type_system as RTS
from ..type_system.bases import standard_base
from .. import abstract_base_classes as ABC
from pathlib import Path
import types

#TODO - move
def is_generator(i):
	return isinstance(i, types.GeneratorType)

#TODO move
def left_shave(line, to_shave):
	if line.startswith(to_shave):
		return line[len(to_shave):]
	else:
		return line


def get_indention_prefix(line, strict=False):
	stripped = line.lstrip('\t ')
	count = len(line) - len(stripped)
	prefix = line[:count]

	if strict and prefix and prefix[0] in '\t ':
		#Check that prefix is not mixed
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

	#Currently we will actually allow mutation and just hope we donä't get a cached property impact.
	#TODO - address this issue! ↑↑↑

	#RQ - methods accepting title should accept title being None

	def __iadd__(self, other):
		self.lines += other.lines
		return self

	lines = RTS.field(factory=list, read_only=False)

	#@RTS.cached_property(lines)
	@property
	def title(self):
		if flc := self.first_line_with_contents:
			return flc.strip()

		#Note that the title is the first line no matter of its indention

	#@RTS.cached_property(lines)
	@property
	def first_line_with_contents(self):
		flc = self.index_of_first_line_with_contents
		if flc is not None:
			return self.lines[flc]

	#@RTS.cached_property(lines)
	@property
	def index_of_first_line_with_contents(self):
		return self.get_index_of_first_line_with_contents()

	def get_indention_level_of_line_index(self, index):	#TODO - support indention settings
		return get_indention_level(self.lines[index])

	def get_indention_prefix_of_line_index(self, index):	#TODO - support indention settings
		return get_indention_prefix(self.lines[index])

	def split_indention_prefix_of_line_index(self, index):
		prefix = self.get_indention_prefix_of_line_index(index)
		return prefix, self.lines[index][len(prefix):]

	@classmethod
	def from_text(cls, text):
		return cls(tuple(text.split('\n')))

	@classmethod
	def from_match(cls, match):
		return cls(tuple(match.group().split('\n')))

	@classmethod
	def from_path(cls, path):
		return cls.from_text(Path(path).read_text())

	@classmethod
	def from_branches(cls, *branches):
		return cls.from_title_and_branches(None, branches)

	@classmethod
	def from_title_and_branches(cls, title, branches):
		if title is None:
			lines = ()
			for b in branches:
				lines += tuple(b.lines)

		else:
			lines = (title,)
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

	#TODO - verify this works properly
	def get_index_of_last_line_with_contents(self, end=-1):
		for rindex, line in enumerate(self.lines[end:0:-1], 0):
			index = len(self.lines) - rindex
			if stripped := line.strip():
				return index



	#TODO - should we implement write, from_pieces and write_pieces?

	def write(self, text):
		if isinstance(text, str):
			ingress, *remaining = text.split('\n')
		elif isinstance(text, text_node):
			ingress, *remaining = text.lines
		else:
			raise TypeError(text)

		if self.lines:
			self.lines[-1] += ingress
		else:
			self.lines.append(ingress)

		self.lines.extend(remaining)


	@classmethod
	def from_pieces(cls, iterator):
		r = cls()
		r.write_pieces(iterator)
		return r

	@classmethod
	def from_blocks(cls, iterator):
		r = cls()
		r.write_blocks(iterator)
		return r

	def write_pieces(self, iterator):
		for i in iterator:
			if is_generator(i):
				self.write_pieces(i)
			else:
				self.write(i)

	def write_blocks(self, iterator):
		for i in iterator:
			if is_generator(i):
				self.write_blocks(i)
			else:
				self += i



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

	#@RTS.cached_property(lines)
	@property
	def body(self):
		return self.get_body(False)

	#@RTS.cached_property(lines)
	@property
	def has_contents(self):
		return bool(self.text.strip())

	#@RTS.cached_property(lines)
	@property
	def text(self):
		#Assumes automatic dedention
		minimum_indention_prefix = get_minimum_indention_prefix(self.lines)
		skip = len(minimum_indention_prefix)
		return '\n'.join(line[skip:] if line.strip() else line for line in self.lines)

	def cleaned_copy(self):
		return self.__class__(self.lines[self.get_index_of_first_line_with_contents():self.get_index_of_last_line_with_contents()]).dedented_copy()

	def dedented_copy(self):
		prefix = get_minimum_indention_prefix(self.lines)
		return self.__class__(tuple(left_shave(l, prefix) for l in self.lines))

	def dedented_lines(self):
		prefix = get_minimum_indention_prefix(self.lines)
		return tuple(left_shave(l, prefix) for l in self.lines)

	def indented_copy(self, prefix='\t'):
		return self.__class__(tuple(f'{prefix}{l}' for l in self.lines))

	def __len__(self):
		return len(tuple(self.iter_nodes()))