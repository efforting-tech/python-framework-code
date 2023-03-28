from .introspection import get_fields, get_public_fields
from ..data_utils import stack_limit
def format_field(target, field_name):
	MISS = object()
	if (value := getattr(target, field_name, MISS)) is not MISS:
		r = repr(value)
		if len(r) > 1500:
			return f'{r[:1490]}\N{HORIZONTAL ELLIPSIS}'
		else:
			return r
	else:
		return 'N/A'


local_fields_stack_limiter = stack_limit(2)

def adjust_field_stack_limit(new_limit):
	global local_fields_stack_limiter
	local_fields_stack_limiter = stack_limit(new_limit)

def local_fields(target):
	with local_fields_stack_limiter:
		try:
			positional = (format_field(target, f.name) for f in get_fields(target.__class__).values() if f.positional)
			named = (f'{f.name}={format_field(target, f.name)}' for f in get_fields(target.__class__).values() if not f.positional)
			inner = ', '.join((*positional, *named))
			return f'{target.__class__.__qualname__}({inner})'

		except RecursionError:
			return '\N{HORIZONTAL ELLIPSIS}'


def local_public_fields(target):
	with local_fields_stack_limiter:
		try:
			positional = (format_field(target, f.name) for f in get_public_fields(target.__class__).values() if f.positional)
			named = (f'{f.name}={format_field(target, f.name)}' for f in get_public_fields(target.__class__).values() if not f.positional)
			inner = ', '.join((*positional, *named))
			return f'{target.__class__.__qualname__}({inner})'

		except RecursionError:
			return '\N{HORIZONTAL ELLIPSIS}'
