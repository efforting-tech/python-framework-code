from .. import Symbol as S
from ..core import record as R
from ..str.interface import String_Interface

tokens = dict(
	left_wrapper = r'«',
	right_wrapper = r'»',
	escaped_left_wrapper = r'\\«',
	escaped_right_wrapper = r'\\»',
	text = None,
)


def repr_value_only(instance, field, info):
	return repr(getattr(instance, field, S.Miss))

class core_token(R.Record):
	value: R.Field(repr=repr_value_only) = ''

	def write(self, value):
		self.value += value

class wrapped(core_token):
	pass

class text(core_token):
	pass


def parse_wrapped(s):
	result = list()
	current = text()
	for token in String_Interface.regex_tokenize(s, tokens):

		if token.token == 'left_wrapper':
			result.append(current)
			current = wrapped()
		elif token.token == 'right_wrapper':
			result.append(current)
			current = text()
		elif token.token == 'escaped_left_wrapper':
			current.write('«')
		elif token.token == 'escaped_right_wrapper':
			current.write('»')
		elif token.token == 'text':
			current.write(token.match.group())
		else:
			raise Exception(token)
	result.append(current)

	return result