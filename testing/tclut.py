from dataclasses import dataclass

class Type_Hook_LUT_KeyError(KeyError):
	def __init__(self, target, key):
		super().__init__(f'{target!r} does not contain any hooks for {key!r}')


class Type_Collection_LUT:
	'Associates types with an ordered set of entries. When enumerating, it respects inheritance, yielding entries from parent types first (reverse MRO).'

	def __init__(self):
		self.LUT = dict()

	def __setitem__(self, key, entry):
		if (existing := self.LUT.get(key)) is None:
			self.LUT[key] = dict.fromkeys((entry,), True)
		else:
			existing[entry] = True

	def __getitem__(self, key):
		if entry := self.LUT.get(key):
			return entry.keys()
		else:
			raise Type_Hook_LUT_KeyError(self, key)

	def __delitem__(self, entry):
		to_del = list()
		for key, entries in self.LUT.items():
			if entry in entries:
				to_del.append((entries, entry))

		for entries, entry in to_del:
			del entries[entry]

	def __contains__(self, key):
		return key in self.LUT

	def get(self, key, default=None):
		if entry := self.LUT.get(key):
			return entry.keys()
		else:
			return default


	def walk_entries(self, type_key):
		for base in reversed(type_key.mro()):
			yield from self.get(base, ())



class Type_Collection_ID_LUT:
	'Associates types with an ordered set of entries based on id() for each entry. When enumerating, it respects inheritance, yielding entries from parent types first (reverse MRO).'

	def __init__(self):
		self.LUT = dict()

	def __setitem__(self, key, entry):
		if (existing := self.LUT.get(key)) is None:
			self.LUT[key] = {id(entry): entry}
		else:
			existing[id(entry)] = entry

	def __getitem__(self, key):
		if entry := self.LUT.get(key):
			return entry.values()
		else:
			raise Type_Hook_LUT_KeyError(self, key)

	def __delitem__(self, entry):
		to_del = list()
		for key, entries in self.LUT.items():
			if entry in entries:
				to_del.append((entries, entry))

		for entries, entry in to_del:
			del entries[entry]

	def __contains__(self, key):
		return key in self.LUT

	def get(self, key, default=None):
		if entry := self.LUT.get(key):
			return entry.values()
		else:
			return default


	def walk_entries(self, type_key):
		for base in reversed(type_key.mro()):
			yield from self.get(base, ())



@dataclass
class Pending_Type_LUT_Entry:
	LUT: Type_Collection_LUT
	entries: list

	def __call__(self, target_type):
		for entry in self.entries:
			self.LUT[entry] = target_type
		return target_type


class Type_Hook_LUT(Type_Collection_LUT):
	def hook(self, *type_list):
		return Pending_Type_LUT_Entry(self, type_list)
