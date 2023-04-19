from ..type_system.bases import public_base
from .. import type_system as RTS
from ..iteration_utils import sliding_slice
import re

#TODO - should we pass context to to_pattern? This part still needs a bit more work
#		we need to both be able to create expressions (and figure out if we want \s+ or \s*
#		We may need to be able to query the pattern for more information as well, such as what captures it is using
#		but for the latter purpose we might just have another member function
#		later on we could use the API feature to make sure API is fully defined
#		In the API enforcing feature we may want stuff like "use parent if function not defined" or "each node needs to define function"



class required_space(public_base):
	def to_string(self):
		return f' '

	def to_pattern(self, context=None):
		return rf'\s+'

	def iter_captures(self):
		yield from ()

class optional(public_base):
	item = RTS.positional()

	def to_string(self):
		return f'[{self.item.to_string()}]'

	def to_pattern(self, context=None):
		return rf'(?:{self.item.to_pattern(context)})?'

	def iter_captures(self):
		yield from self.item.iter_captures()


class literal_text(public_base):
	text = RTS.positional()

	def to_pattern(self, context=None):
		return re.escape(self.text)


	def to_string(self):
		return self.text

	def iter_captures(self):
		yield from ()

class capture(public_base):
	name = RTS.positional()

	def iter_captures(self):
		yield self

# class pending_capture(public_base):
# 	text = RTS.positional()

class option(public_base):
	value = RTS.positional()

class specified_capture(public_base):
	capture = RTS.positional()
	options = RTS.all_positional()

class remaining_words(capture):
	greedy = RTS.setting(True)

	def to_string(self):
		g = '?' if not self.greedy else ''
		return f'{{*{self.name}{g}}}'

	def to_pattern(self, context=None):
		g = '?' if not self.greedy else ''
		if context is None:
			return rf'(?P<{self.name}>.+{g})'
		else:
			return rf'(?P<{context.register_capture(self, self.name)}>.+{g})'

class remaining_text(capture):
	greedy = RTS.setting(True)

	def to_string(self):
		g = '?' if not self.greedy else ''
		return f'{{{self.name}...{g}}}'

	def to_pattern(self, context=None):
		g = '?' if not self.greedy else ''
		if context is None:
			return rf'(?P<{self.name}>.*{g})'
		else:
			return rf'(?P<{context.register_capture(self, self.name)}>.*{g})'


class specific_word(capture):
	def to_string(self):
		return f'{{{self.name}}}'

	def to_pattern(self, context=None):
		if context is None:
			return rf'(?P<{self.name}>\w+)'
		else:
			return rf'(?P<{context.register_capture(self, self.name)}>\w+)'

class specific_dotted_identifier(capture):
	def to_string(self):
		return f'{{.{self.name}}}'

	def to_pattern(self, context=None):
		if context is None:
			return rf'(?P<{self.name}>[\w\.]+)'
		else:
			return rf'(?P<{context.register_capture(self, self.name)}>[\w\.]+)'

class sequential_pattern(public_base):
	sequence = RTS.all_positional()

	def to_string(self):
		return ''.join(i.to_string() for i in self.sequence)

	def to_pattern(self, context=None):
		return ''.join((i.to_pattern(context) for i in self.sequence))


		# seq = tuple(i.to_pattern(context) for i in self.sequence)

		# #This is a bit of an uggly hack - to solve this properly we need to setup more advanced rules, for instance 'a [b][c] d' should be 'a[\s+b][\s+c]\s+d' - so we need to be able to pad insides of captures
		# result = seq[0]
		# for (previous, next), pattern in zip(sliding_slice(self.sequence, 2), seq[1:]):
		# 	if isinstance(previous, optional) or isinstance(next, optional):
		# 		result += rf'\s*{pattern}'
		# 	else:
		# 		result += rf'\s+{pattern}'


		# return result

	def iter_captures(self):
		for sub_item in self.sequence:
			yield from sub_item.iter_captures()