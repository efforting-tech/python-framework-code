from collections.abc import Mapping

def iter_public_items(source):
	if isinstance(source, Mapping):
		yield from ((key, value) for key, value in source.items() if not key.startswith('_'))
	else:
		yield from ((key, value) for key, value in source.__dict__.items() if not key.startswith('_'))

def iter_public_values(source):
	if isinstance(source, Mapping):
		yield from (value for key, value in source.items() if not key.startswith('_'))
	else:
		yield from (value for key, value in source.__dict__.items() if not key.startswith('_'))
