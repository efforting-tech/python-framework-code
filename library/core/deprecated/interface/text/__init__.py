
class Core_Line_Interface:
	@property
	def indent(self):
		return len(self.text) - len(self.text.lstrip('\t'))


class Core_Line_View_Interface:
	@classmethod
	def from_str(cls, value):
		return cls(value.splitlines())

	def __len__(self):
		return len(self.lines)

	def __iter__(self):
		yield from self.lines

	def __getitem__(self, index_or_slice):
		print(index_or_slice)
		assert isinstance(index_or_slice, int), 'Slices not supported at core'
		return self.lines[index_or_slice]


class Immutable_Line_View_Interface(Core_Line_View_Interface):
	pass

class Mutable_Line_View_Interface(Core_Line_View_Interface):
	pass