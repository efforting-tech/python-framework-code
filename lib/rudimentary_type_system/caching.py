NOT_ASSIGNED = object() #TODO symbol


class cached_property_handler:
	def __init__(self, cache_field, key_fields, function):
		self.cache_field = cache_field
		self.key_fields = key_fields
		self.function = function

	def __call__(self, instance):
		key = tuple(instance.__dict__.get(f.name, NOT_ASSIGNED) for f in self.key_fields)

		if cache := getattr(instance, self.cache_field, None):
			cached_key, cached_value = cache
			if cached_key == key:
				return cached_value

		value = self.function(instance)
		cache = key, value
		setattr(instance, self.cache_field, cache)
		return value

class cached_property:
	def __init__(self, *key_fields):
		self.key_fields = key_fields

	def __call__(self, function):
		for field in self.key_fields:
			assert field.read_only, f'{self.__class__} can only be used with immutable key fields which {field} is not'

		return property(fget=cached_property_handler(f'_{function.__name__}' , self.key_fields, function))
