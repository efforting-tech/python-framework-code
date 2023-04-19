from ..symbols import register_symbol
from ..type_system.introspection import get_fields
from collections.abc import Mapping
import types

MISS = register_symbol('internal.miss')

def space_wrap(item):
	result = str(item)
	if ' ' in result:
		return f'({result})'
	else:
		return result


class space_wrapping_object_accessor(Mapping):
	def __init__(self, target):
		self.target = target

	class builtin_formatters:
		def format_operands(target, operands):
			return space_wrap(', '.join(space_wrap(op) for op in operands))

		def format_container(target, *contents):
			formatted_contents = ', '.join(map(space_wrap, contents))
			return f'{target.__class__.__name__}({formatted_contents})'

		def format_joined(target, separator, *contents):
			return separator.join(map(space_wrap, contents))


	def __getitem__(self, key):
		if key == '_':
			return self.target

		elif builtin := getattr(self.builtin_formatters, key, None):
			return types.MethodType(builtin, self.target)

		elif (value := getattr(self.target, key, MISS)) is not MISS:
			return space_wrap(value)

		elif key in get_fields(self.target.__class__):
			return '?'
		else:
			raise AttributeError(represent_local_fields(self.target), key)

	def __iter__(self):
		yield from get_fields(self.target.__class__)

	def __len__(self):
		return len(get_fields(self.target.__class__))



