#Deprecate this module?

raise NotImplementedError("This feature needs additional planning or may be deprecated or replaced")	#TODO - make decision


#import itertools
from collections import namedtuple
#from .tabular_utils import fields_from_specifiers



#Note - we did some experiments with a specific case for 1-1 with no_unary_containers
#	but it gets messy and it is better to have a specific type for a class that does not utilize on multiple maps to one record

#This does not implement any caching since in this use case we will not really benefit from that but we should for later
#Note - we will want many different but similar ones
#	- strict ones that only allow something once in every column
#	- one that uses identity_reference for all items
#	- ...


#NOTE: The combinations are not needed for the strict one
# for length in range(1, len(fields)):
# 	for p in itertools.combinations(fields, length):
# 		name = '_and_'.join(p)
# 		setattr(self, f'by_{name}', strict_tabular_mapping_selection(self, p))


class strict_tabular_mapping_selection:
	def __init__(self, owner, lut, index):
		self.owner = owner
		self.lut = lut
		self.index = index

	def __getitem__(self, key):
		return self.lut[key]

	def __setitem__(self, key, values):

		#Create new entry
		new_entry = self.owner._entry_type(*values)

		#Check that new entry is consistent with key
		assert new_entry[self.index] == key

		#First check that we have no conflict
		if existing := self.lut.get(key):
			#We must check that we can do this update without affecting any records that is not the existing one - then we can swap it out
			for (field, lut), pending_value in zip(self.owner._lut_map.items(), values):
				if (conflict_entry := lut.get(pending_value)) and conflict_entry is not existing:
					raise Exception(f'Conflict detected for field {field!r}, {pending_value!r} already in column')

			#Now we can simply update the luts to point to the new one
			for lut, pending_value in zip(self.owner._lut_map.values(), values):
				lut[pending_value] = new_entry

		else:
			self.owner.append(*values)

	def __contains__(self, key):
		return key in self.lut

	#TODO __delitem__

	def get(self, key, default=None):
		return self.lut.get(key, default)


	def pop(self, key, default=None):
		#Assumes data is kept consistant
		MISS = object()
		if (entry := self.lut.get(key, MISS)) is MISS:
			return default

		for lut, value in zip(self.owner._lut_map.values(), entry):
			lut.pop(value)

		return entry


class strict_tabular_mapping:
	_selection_type = strict_tabular_mapping_selection

	def __init__(self, *field_specifiers):
		fields = fields_from_specifiers(field_specifiers)
		name_suffix = '_'.join(fields)
		self._entry_type = namedtuple(f'stm_entry_{name_suffix}', fields)

		lut_map = dict()
		for index, name in enumerate(fields):
			lut_map[name] = lut = dict()
			setattr(self, f'_by_{name}', lut)
			setattr(self, f'by_{name}', self.__class__._selection_type(self, lut, index))

		self._lut_map = lut_map

	def append(self, *values):
		#First check that we have no conflict
		for (field, lut), value in zip(self._lut_map.items(), values):
			assert value not in lut

		#Create new entry
		entry = self._entry_type(*values)

		#Update tables
		for lut, value in zip(self._lut_map.values(), values):
			lut[value] = entry

	def __iter__(self):
		yield from next(iter(self._lut_map.values())).values()

	def update(self, *values):
		#This is like append but we are ok with a conflict as long as they all resolve to the same entry

		#Start by checking for ambiguity of the entry
		previous_entry = None
		for (field, lut), value in zip(self._lut_map.items(), values):
			if candidate := lut.get(value):
				if previous_entry is None:
					previous_entry = candidate
				elif previous_entry is not candidate:
					raise Exception(f'Ambiguous entry {values!r}')

				if (conflict_entry := lut.get(value)) and conflict_entry is not previous_entry:
					raise Exception(f'Conflict detected for field {field!r}, {pending_value!r} already in column')

		#Create new entry
		new_entry = self._entry_type(*values)

		if previous_entry:
			#Remove old entries
			for lut, value in zip(self._lut_map.values(), previous_entry):
				lut.pop(value)

		#Update tables
		for lut, value in zip(self._lut_map.values(), values):
			lut[value] = new_entry

	def __contains__(self, values):
		lut = next(iter(self._lut_map.values()))

		if (candidate := lut.get(values[0])) and candidate == values:
			return True

	#TODO __delitem__ ?

	def clear(self):
		for lm in self._lut_map.values():
			lm.clear()



#TODO: 1:1 mapping - possibly (partly?) derived from strict_tabular_mapping via templating.

class strict_binary_mapping_selection:
	def __init__(self, owner, lut, index):
		self.owner = owner
		self.lut = lut
		self.index = index

	def __getitem__(self, key):
		if self.index == 0:
			return self.lut[key][1]
		elif self.index == 1:
			return self.lut[key][0]
		else:
			raise Exception()

	def __setitem__(self, key, value):
		#Create new entry
		if self.index == 0:
			new_entry = self.owner._entry_type(key, value)
		elif self.index == 1:
			new_entry = self.owner._entry_type(value, key)
		else:
			raise Exception()


		#Check that new entry is consistent with key
		assert new_entry[self.index] == key

		#First check that we have no conflict
		if existing := self.lut.get(key):
			#We must check that we can do this update without affecting any records that is not the existing one - then we can swap it out
			for (field, lut), pending_value in zip(self.owner._lut_map.items(), new_entry):
				if (conflict_entry := lut.get(pending_value)) and conflict_entry is not existing:
					raise Exception(f'Conflict detected for field {field!r}, {pending_value!r} already in column')

			#Now we can simply update the luts to point to the new one
			for lut, pending_value in zip(self.owner._lut_map.values(), new_entry):
				lut[pending_value] = new_entry

		else:
			self.owner.append(*new_entry)

	def __contains__(self, key):
		return key in self.lut

	#TODO __delitem__

	def get(self, key, default=None):
		MISS = object()
		if (entry := self.lut.get(key, MISS)) is MISS:
			return default
		elif self.index == 0:
				return entry[1]
		elif self.index == 1:
			return entry[0]
		else:
			raise Exception()


	def pop(self, key, default=None):
		#Assumes data is kept consistant
		MISS = object()
		if (entry := self.lut.get(key, MISS)) is MISS:
			return default

		for lut, value in zip(self.owner._lut_map.values(), entry):
			lut.pop(value)

		if self.index == 0:
			return entry[1]
		elif self.index == 1:
			return entry[0]
		else:
			raise Exception()



class strict_binary_mapping(strict_tabular_mapping):
	_selection_type = strict_binary_mapping_selection
