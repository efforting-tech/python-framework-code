from ..abstract_base_classes import auto_conversion as A
from collections import namedtuple


#TODO create exceptions

AUTO = object()

class generic_key:
	def __init__(self, owner, name, indices, unique, view):
		self.owner = owner
		self.name = name
		self.indices = indices
		self.unique = unique
		self.view = view
		self.lut = dict()

	def validate_pending_entry(self, entry):
		if self.unique:
			key = self.get_key(entry)
			if key in self.lut:
				return False

		return True

	def register_entry(self, entry):
		#NOTE - expects entry to have passed validation
		key = self.get_key(entry)
		if self.unique:
			self.lut[key] = entry
		else:
			if el := self.lut.get(key):
				el.append(entry)
			else:
				self.lut[key] = [entry]

	def get(self, key, default=None):

		if value := self.lut.get(key):

			if self.view is not None:
				if len(self.view) == 1:
					[return_index] = self.view

					if self.unique:
						return value[return_index]
					else:
						return tuple(v[return_index] for v in value)
				else:
					if self.unique:
						return tuple(value[ri] for ri in self.view)
					else:
						return tuple(tuple(v[ri] for ri in self.view) for v in value)

			if self.unique:
				return value
			else:
				return tuple(value)
		else:
			return default

	def __contains__(self, key):
		return key in self.lut

	def __getitem__(self, key):

		value = self.lut[key]

		if self.view is not None:
			if len(self.view) == 1:
				[return_index] = self.view

				if self.unique:
					return value[return_index]
				else:
					return tuple(v[return_index] for v in value)
			else:
				if self.unique:
					return tuple(value[ri] for ri in self.view)
				else:
					return tuple(tuple(v[ri] for ri in self.view) for v in value)

		if self.unique:
			return value
		else:
			return tuple(value)

	def __delitem__(self, key):
		self.owner.delete(self.lut[key])


	def __setitem__(self, raw_key, value):

		if self.view is None:
			if isinstance(value, self.owner.entry_type):
				entry = value
			else:
				entry = self.owner.entry_type(*value)

		else:

			if isinstance(value, self.owner.entry_type):
				entry = value
			else:
				if len(self.view) == 1:
					[vi] = self.view
					entry_pieces = dict(((vi, value), *self.iter_key_index_pairs(raw_key)))
				else:
					entry_pieces = dict((*self.iter_key_index_pairs(raw_key), *zip(self.view, value)))

				entry = self.owner.entry_type(*(entry_pieces.pop(i) for i in range(len(self.owner.entry_type._fields))))
				assert not entry_pieces


		key = self.get_key(entry)
		assert key == raw_key

		#TODO - we may want to change how this works because now we could delete something to then fail to add something
		#		but the problem is that if we are checking the key requirements we may fail when doing an update
		#		maybe the key check could have support for a pending value to prevent this from being a problem

		if self.unique and (existing := self.lut.get(key)):
			#We must remove existing from all keys
			self.owner.delete(existing)

			#del self.owner.rows[self.owner.rows.index(existing)]

		self.owner.append(entry)

		# for check_key in self.owner.keys.values():
		# 	if not check_key.validate_pending_entry(entry):
		# 		raise Exception(f'Failed validation for key {check_key.name!r} when adding row {entry}.')

		# self.lut[key] = entry
		# self.owner.rows.append(entry)

class multi_field_key(generic_key):

	def get_key(self, entry):
		return tuple(entry[i] for i in self.indices)


class regular_key(generic_key):

	def iter_key_index_pairs(self, key):
		yield (self.indices, key)


	def get_key(self, entry):
		return entry[self.indices]


class generic_tabular_mapping:
	def __init__(self, *field_specifiers, keys=AUTO, unique=None, views=None):
		self.fields = fields = A.collection.identifiers(field_specifiers)
		name_suffix = '_'.join(fields)
		self.entry_type = namedtuple(f'gtm_entry_{name_suffix}', fields)
		self.rows = list()	#Make private?
		self.keys = dict()	#Make private?

		if keys is AUTO:
			#Generate a key for each field
			for index, name in enumerate(fields):

				#TODO - harmonize with below
				if views and (view_fields := views.get(name)):
					key_view = tuple(fields.index(f) for f in A.collection.identifiers(view_fields))
				else:
					key_view = None	#TODO


				key = self.keys[name] = regular_key(self, name, index, name in fields, key_view)
				setattr(self, f'by_{name}', key)

		elif keys is None:
			pass

		else:
			for name, key_spec in keys.items():
				key_fields = A.collection.identifiers(key_spec)

				#TODO - harmonize with above
				if views and (view_fields := views.get(name)):
					key_view = tuple(fields.index(f) for f in A.collection.identifiers(view_fields))
				else:
					key_view = None	#TODO


				if len(key_fields) == 1:
					[kf] = key_fields
					key = self.keys[name] = regular_key(self, name, self.fields.index(kf), name in fields, key_view)
				else:
					indices = tuple(self.fields.index(kf) for kf in key_fields)
					key = self.keys[name] = multi_field_key(self, name, indices, name in fields, key_view)

				setattr(self, f'by_{name}', key)

	def append(self, *values):
		if len(values) == 1 and isinstance(values[0], self.entry_type):
			[entry] = values
		else:
			entry = self.entry_type(*values)

		for key in self.keys.values():
			if not key.validate_pending_entry(entry):
				raise Exception(f'Failed validation for key {key.name!r} when adding row {entry}.')

		for key in self.keys.values():
			key.register_entry(entry)

		self.rows.append(entry)

	def delete(self, entry):
		#Note - this isn't using a LUT and will be slow for large datasets - possibly we should use a set here that works on the identity of the entry
		#		but there might still be cases where we need to find an entry (but that should be possible to speed up using the lowest cardinality key)
		#		but such advanced features are currently outside of the scope of this feature that aims to provide a generic
		#		way of dealing with tables

		del self.rows[self.rows.index(entry)]
		for key in self.keys.values():
			key.lut.pop(key.get_key(entry))

#TODO - Prioritize documenting this feature with examples
def one_to_one_mapping(*field_specifiers):
	F = (a, b) = A.collection.identifiers(field_specifiers)
	return generic_tabular_mapping(F, unique=F, views={a: b, b: a})

#TODO - Prioritize documenting this feature with examples
def strict_unique_mapping(*field_specifiers):
	F = A.collection.identifiers(field_specifiers)
	return generic_tabular_mapping(F, unique=F)
