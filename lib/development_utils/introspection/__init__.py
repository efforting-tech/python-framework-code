from ...type_system.bases import standard_base
from ...type_system.introspection import get_fields

def introspect(item):
	match item:
		case type() if issubclass(item, standard_base):
			print(f'Class {item.__module__}.{item.__qualname__}')
			for field in get_fields(item).values():
				if field.owner:
					print(f'    {field.name}: {field.__class__.__name__!r} defined in {field.owner.__name__!r}')
				else:
					print(f'    {field.name}: {field.__class__.__name__!r}')
