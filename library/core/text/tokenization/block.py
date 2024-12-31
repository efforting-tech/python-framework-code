from ... import records as R, Symbol as S

def local_slice_to_line_range(start, stop, first, last):
	"""
	Calculate the line range from a slice's start and stop values,
	given the extent of the parent block.

	Args:
		start (int or None): Start of the slice (can be None for full extent or negative for reverse indexing).
		stop (int or None): Stop of the slice (can be None for full extent or negative for reverse indexing).
		first (int): First line of the parent block.
		last (int): Last line of the parent block.

	Returns:
		tuple: A tuple of (first_line, last_line) representing the slice result.

	This function was written by ChatGPT 4o by OpenAI
	"""

	if last < first:	#Return on empty block
		return (first, last)

	# Handle None for start and stop to indicate full extent
	adjusted_start = first if start is None else (last + 1 + start if start < 0 else first + start)
	adjusted_stop = last + 1 if stop is None else (last + 1 + stop if stop < 0 else first + stop)

	# Adjust for slice exclusivity (stop is exclusive in slice notation)
	adjusted_stop -= 1

	# Ensure bounds are within the parent block
	adjusted_start = max(first, min(adjusted_start, last + 1))
	adjusted_stop = max(first - 1, min(adjusted_stop, last))


	return (adjusted_start, adjusted_stop)

def absolute_slice_to_line_range(start, stop, first, last):
	if last < first:	#Return on empty block
		return (first, last)

	# Handle None for start and stop to indicate full extent
	adjusted_start = first if start is None else (last + 1 + start if start < 0 else start)
	adjusted_stop = last + 1 if stop is None else (last + 1 + stop if stop < 0 else stop)

	return (adjusted_start, adjusted_stop)



class Block(R.Record):
	document: R.Field()	#TODO - read only
	first_line: R.Field() = 0	#TODO - read only
	last_line: R.Field(factory='_init_last_line')	#TODO - read only

	def __bool__(self):
		return len(self) > 0

	def __len__(self):
		return max(0, self.last_line - self.first_line + 1)

	def _init_last_line(self):
		return len(self.document) - 1

	def absolute_sub_block(self, first_line, last_line):
		return Block(self.document, *absolute_slice_to_line_range(first_line, last_line, self.first_line, self.last_line))


	def __getitem__(self, index_or_slice):
		match index_or_slice:
			case slice(start=start, stop=stop, step=step) if step in (1, None):
				return Block(self.document, *local_slice_to_line_range(start, stop, self.first_line, self.last_line))

			case slice():
				raise NotImplementedError(f'Slices with stepsizes other than 1 are not supported')

			case int():
				return self.document[self.first_line +  index_or_slice]

			case otherwise:
				raise TypeError(otherwise)

	@property
	def tokens(self):
		d = self.document
		return d.tokens[d[self.first_line].start:d[self.last_line].end+1]

	@property
	def span(self):
		return self.first_line, self.last_line

	# @property
	# def parent_slice(self):
	# 	return slice(self.first_line, self.last_line + 1)

	@property
	def text(self):
		d = self.document
		l, r = d.tokens[d[self.first_line].start], d.tokens[d[self.last_line].end]
		return self.document.text[l.match.start():r.match.end()]	#NOTE - for match statements end() is like with a slice but for first_line last_line we consider both endpoints to be part of the span.

	#TODO - decide if we want this or not. One problem is during introspection where things are str(stuff) rather than repr(stuff) by default.
	#def __str__(self):
	#	return self.text


	def iter_relative_lines(self, only_with_content=False):
		for index in range(len(self)):  #range(self.first_line, self.last_line + 1):
			line = self.document[index + self.first_line]
			if only_with_content and not line.body_span:
				continue
			yield (index, line)


	def iter_absolute_lines(self, only_with_content=False):
		for index in range(self.first_line, self.last_line + 1):
			line = self.document[index]
			if only_with_content and not line.body_span:
				continue
			yield (index, line)
