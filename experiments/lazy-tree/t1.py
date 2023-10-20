from efforting.mvp4.rudimentary_types.data_path import data_path
import sys, fnmatch

class lazy_value:
	def __init__(self, loader):
		self.loader = loader
		self.is_loaded = False
		self.value = None

	def get(self):
		if self.is_loaded:
			return self.value
		else:
			value = self.value = self.loader()
			self.is_loaded = True
			return self.value

class pending_lazy_tree_loader:
	def __init__(self, tree, path):
		self.tree = tree
		self.path = path

	def __call__(self, function):
		self.tree[self.path] = lazy_value(function)

class lazy_tree_accessor:
	def __init__(self, tree):
		self._tree = tree

	def __getattr__(self, name):
		value = self._tree.children[name]
		if isinstance(value, lazy_tree):
			return value.accessor
		elif isinstance(value, lazy_value):
			return value.get()
		else:
			return value

class lazy_tree:
	def __init__(self, name=None, parent=None):
		self.name = name
		self.parent = parent
		self.children = dict()

	def export(self, *pattern_list, stack_offset=0):
		target = sys._getframe(stack_offset+1).f_locals
		exported = dict()
		for path, value in self.root.deep_iter_leaves():
			for pattern in pattern_list:
				if fnmatch.fnmatch(path, pattern):
					assert path.name not in exported, f'Ambiguous leaves detected for patterns {pattern_list!r}: {path}'
					exported[path.name] = value.get()
					break

		target.update(exported)


	@property
	def root(self):
		if self.parent:
			return self.parent.root
		else:
			return self

	def deep_iter_leaves(self):
		for child_name, child_value in self.children.items():
			if isinstance(child_value, lazy_tree):
				yield from child_value.deep_iter_leaves()
			else:
				yield self.path / child_name, child_value

	@property
	def accessor(self):
		return lazy_tree_accessor(self)

	def assign_loader(self, path):
		return pending_lazy_tree_loader(self, path)

	def branch(self, name):
		assert name not in self.children
		branch = self.children[name] = self.__class__(name, self)
		return branch

	def get(self, name):
		return self.children.get(name)

	def set_value(self, name, value):
		assert name not in self.children
		self.children[name] = value

	@property
	def path(self):
		if self.parent:
			return self.parent.path / self.name
		elif self.name:
			return data_path(self.name)
		else:
			return data_path()

	def __setitem__(self, path, value):
		ptr = self
		pending_parts = list(data_path(path).parts)
		leaf_name = pending_parts.pop(-1)
		for part in pending_parts:
			if existing_child := ptr.get(part):
				ptr = existing_child
			else:
				ptr = ptr.branch(part)

		ptr.set_value(leaf_name, value)

	def __getitem__(self, path):
		ptr = self
		for part in data_path(path).parts:
			if existing_child := ptr.get(part):
				ptr = existing_child
			else:
				raise Exception(f'{ptr.path!r} does not have a member {part!r}')

		return ptr

tree = lazy_tree()

@tree.assign_loader('path.to.some.string')
def loader():
	'This is some string'
	return 'some string'

@tree.assign_loader('path.to.math')
def loader():
	import math
	return math

@tree.assign_loader('other.math')
def loader():
	return 'othermath'

#Qyery info about an item (loaded or not)
print(tree['path.to.some.string'].loader.__doc__)

#Export items to this (calling) frame using glob expressions
tree.export('path*math', '*string')
print(math, string)

#Create accessor to make it easy to access objects (which are loaded if they are not already loaded)
root = tree.accessor
print(root.path.to.math)