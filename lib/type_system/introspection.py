from .rts_types import field

def get_fields(target):
	field_names = dict()
	for base in reversed(target.mro()):
		for item in base.__dict__.values():
			if isinstance(item, field):
				field_names[item.name] = item

	return field_names

def get_public_fields(target):
	field_names = dict()
	for base in reversed(target.mro()):
		for item in base.__dict__.values():
			if isinstance(item, field) and not item.name.startswith('_'):
				field_names[item.name] = item

	return field_names
