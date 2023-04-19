from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.bases import public_base
from efforting.mvp4.text_nodes import text_node
from efforting.mvp4.table_processing.table import table

from warnings import warn


class raw_include(public_base):
	specifier = RTS.positional()


class file(public_base):
	path = RTS.positional()
	members = RTS.all_positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}(`{self.path}´ {len(self.members)} members)'


class loaded_tree(file):
	pass

class group(public_base):
	name = RTS.positional()
	members = RTS.all_positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}(`{self.name}´ {len(self.members)} members)'

class abstract_listing_of_type(public_base, abstract=True):
	type = RTS.positional()
	name = RTS.positional()
	members = RTS.all_positional()

class list_of_type(abstract_listing_of_type):
	def __repr__(self):
		return f'{self.__class__.__qualname__}(`{self.name}´ (list of `{self.type.lower()}´) {len(self.members)} members)'

class mode_of_type(abstract_listing_of_type):
	def __repr__(self):
		return f'{self.__class__.__qualname__}(`{self.name}´ (mode of `{self.type.lower()}´) {len(self.members)} members)'


class named_table(public_base):
	name = RTS.positional()
	table = RTS.positional()

	@RTS.initializer
	def load_pending_table(self):
		match self.table:
			case text_node():
				self.table = table.from_raster(self.table.text)
			case str():
				self.table = table.from_raster(self.table)

class structure_table(named_table):
	pass


class structure(group):
	pass

class named_option(group):
	pass

class concept(group):
	pass

class feature(group):
	pass

class c_implementation(group):
	pass

class c_source(group):
	pass

class c_header(group):
	pass

class list_of_items(public_base):
	members = RTS.all_positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}({len(self.members)} members)'

	@classmethod
	def from_string(cls, string):
		stripped_sub_items = (i.strip() for i in string.split(','))
		return cls(*(i for i in stripped_sub_items if i))

	@classmethod
	def from_anything(cls, *source_list):
		result = list()
		for source in source_list:
			match source:
				case str():
					result.extend(cls.from_string(source).members)
				case text_node():
					result.extend(cls.from_string(','.join(source.lines)).members)
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')

		return cls(*result)


class stub(group):

	@RTS.initializer
	def generate_warning(self):
		warn(f'{self} encountered')

class required_features(list_of_items):
	pass


class list_of_files(list_of_items):
	#TODO - we need to parse this using a specific file
	@classmethod
	def from_string(cls, string):
		raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature

		#stripped_sub_items = (i.strip() for i in string.split(','))
		#return cls(*(i for i in stripped_sub_items if i))

	@classmethod
	def from_raw(cls, *source_list):
		stripped_sub_items = (source.strip() for source in source_list)
		return cls(*(raw_include(i) for i in stripped_sub_items if i))




	@classmethod
	def from_anything(cls, *source_list):

		return stub(f'{cls.__qualname__}.from_anything', cls, source_list)

		result = list()
		for source in source_list:
			match source:
				case str():
					raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
					#result.extend(cls.from_string(source).members)
				case text_node():
					raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
					#result.extend(cls.from_string(','.join(source.lines)).members)
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')

		return cls(*result)


class include_tree(list_of_files):
	pass

class c_includes(list_of_files):
	pass




class heading(public_base, abstract=True):
	members = RTS.all_positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}({len(self.members)} members)'

class introduction(heading):
	pass

class document(heading):
	pass

class text(public_base):
	value = RTS.positional()

	def __repr__(self):
		return f'{self.__class__.__qualname__}({len(self.value.lines)} lines)'



class note(public_base):
	brief = RTS.positional()
	text = RTS.positional()

	def __repr__(self):
		if self.brief:
			return f'{self.__class__.__qualname__}(`{self.brief}´ {len(self.text.lines)} lines)'
		else:
			return f'{self.__class__.__qualname__}({len(self.text.lines)} lines)'


class brief(note):
	pass


class purpose(note):
	pass

class examples(note):
	pass
