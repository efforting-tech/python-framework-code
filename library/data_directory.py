from pathlib import PurePosixPath, PureWindowsPath, Path
from .data_path import data_path
from .constants import UNDEFINED, ACTION


class generic_data_directory_accessor:
	def __init__(self, directory):
		self._directory = directory

	def __getattr__(self, name):
		if not name.startswith('_'):
			if (candidate := self._directory[name]) is not UNDEFINED:
				return candidate

		raise AttributeError(f'{self._directory} have no attribute {name!r}')

class generic_data_directory:
	path_type = data_path

	def __init__(self, name=None, value=UNDEFINED, children=None, parent=None, lazy_loader=None):
		self.value = value
		self.name = name
		self.parent = parent
		self.lazy_loader = lazy_loader
		if children is None:
			self.children = dict()
		else:
			self.children = children

	def __contains__(self, key):
		p = self
		for item in self.path_type(key).parts:
			if p := p.children.get(item):
				continue
			else:
				return False

		return True

	def __setitem__(self, key, value):
		p = self
		for item in self.path_type(key).parts:
			p = p.get_or_create_child_entry(item)

		p.value = value

	def __getitem__(self, key):
		p = self
		for item in self.path_type(key).parts:
			if p := p.children.get(item):
				continue
			else:
				raise Exception(f'Path {key} was not found in {self}')

		if self.lazy_loader:
			if (potential_new_value := self.lazy_loader(p.value)) is not p.value:
				p.value = potential_new_value

		return p.value

	def update(self, other):
		for item in other.walk():
			if item.value is not UNDEFINED:
				self[item.path] = item.value

	def cast_path(self, path):
		return self.path_type(path)


	def get_directory(self, key, default=ACTION.RAISE_EXCEPTION):
		p = self
		for item in self.path_type(key).parts:
			if p := p.children.get(item):
				continue
			elif default is ACTION.RAISE_EXCEPTION:
				raise Exception(f'Path {key} was not found in {self}')
			else:
				return default

		return p


	@property
	def path(self):
		if not self.name:
			return self.path_type()

		if self.parent:
			return self.path_type(self.parent.path, self.name)
		else:
			return self.path_type(self.name)

	@property
	def root(self):
		if self.parent:
			return self.parent.root
		else:
			return self

	def get_or_create_child_entry(self, name):
		if child := self.children.get(name):
			return child
		else:
			child = self.children[name] = self.__class__(name, parent=self)
			return child

	def get_or_create_value(self, path, factory):

		if entry := self.get_directory(path, None):
			if entry.value is UNDEFINED:
				result = entry.value = factory()
				return result
			else:
				return entry.value
		else:
			result = self[path] = factory()
			return result

	def create_value(self, path, factory):

		if entry := self.get_directory(path, None):
			if entry.value is UNDEFINED:
				result = entry.value = factory()
				return result
			else:
				raise Exception(f'{self} already contains a value for {path!r}')
		else:
			result = self[path] = factory()
			return result


	def walk_depth_first(self, include_undefined=True):
		for child in self.children.values():
			yield from child.walk_depth_first(include_undefined)

		if include_undefined or self.value is not UNDEFINED:
			yield self

	def walk_bredth_first(self, include_undefined=True):
		if include_undefined or self.value is not UNDEFINED:
			yield self

		for child in self.children.values():
			yield from child.walk_bredth_first(include_undefined)

	def to_dict(self, include_undefined=False):
		return {entry.path: entry.value for entry in self.walk(include_undefined)}



	#SKETCH - do we want it?
	def create_attribute_based_registration_decorator(self, attribute):
		return attribute_based_registration_decorator(self, attribute)


	#SKETCH - do we want it? (It's for use as a decorator)
	@property
	def register(self):
		return generic_registration_decorator(self)

	@property
	def root_accessor(self):
		return generic_data_directory_accessor(self)


	walk = walk_bredth_first

class path_data_directory(generic_data_directory):
	path_type = Path

class pure_posix_path_data_directory(generic_data_directory):
	path_type = PurePosixPath

class pure_windows_path_data_directory(generic_data_directory):
	path_type = PureWindowsPath
