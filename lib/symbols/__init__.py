from ..pre_rts import pre_rts_type, rts_factory
from ..rudimentary_types.data_path import data_path

#Currently we register symbol here and there and the problem with that is that we may make mistakes that we don't realize. We should define them all in one spot then refer to them here and there

class symbol_node(pre_rts_type):
	_default_values = dict(
		name = None,
		parent = None,
		children = rts_factory(dict),
		prefix = None,
	)

	def walk(self):
		yield self
		for child in self.children.values():
			yield from child.walk()

	def create_symbol(self, path):
		ptr = self
		for piece in data_path(path).parts:
			if not piece.isidentifier():
				raise ValueError(f'Path {path!r} contains non identifiers')
			if pending := ptr.children.get(piece):
				ptr = pending
			else:
				parent = ptr
				ptr = parent.children[piece] = self.__class__(name=piece, parent=parent)

		return ptr

	def require_symbol(self, path):
		ptr = self
		for piece in data_path(path).parts:
			if not piece.isidentifier():
				raise Exception()
			if pending := ptr.children.get(piece):
				ptr = pending
			else:
				raise Exception(f'Required symbol {path!r} not found in {self!r}.')

		return ptr

	def get_symbol(self, path, default=None):
		ptr = self
		for piece in data_path(path).parts:
			if not piece.isidentifier():
				return default
			if pending := ptr.children.get(piece):
				ptr = pending
			else:
				return default

		return ptr

	@property
	def root(self):
		if self.parent:
			return self.parent.root
		else:
			return self

	@property
	def path(self):
		if self.parent and self.parent.name:
			return self.parent.path / self.name
		elif self.name:
			return data_path(self.name)
		else:
			return data_path()

	def __repr__(self):

		if self.prefix:
			if self.name:
				return f'{self.prefix}:{self.__class__.__name__}({hex(id(self.root))} {self.path})'
			else:
				return f'{self.prefix}:{self.__class__.__name__}({hex(id(self.root))} (root))'
		else:

			if self.name:
				return f'{self.__class__.__name__}({hex(id(self.root))} {self.path})'
			else:
				return f'{self.__class__.__name__}({hex(id(self.root))} (root))'


#TODO - this should use proxy resolution
class symbol_attribute_access_interface:
	def __init__(self, target):
		self._target = target


	def __getattr__(self, name):
		if symbol := self._target.get_symbol(name):
			return self.__class__(symbol)
		else:
			raise AttributeError(self, name)


	#This is so that we can use this interchangeably with the targets (this is similar to the TBI identity_reference)
	def __eq__(self, other):
		return self._target == other

	def __hash__(self):
		return hash(self._target)


class symbol_tree_node(symbol_attribute_access_interface):
	def __repr__(self):
		return f'`{self._target.path}´'

	def __call__(self, name=None):
		#TODO - explain why (consider __set_name__)
		if name:
			return symbol_tree_node(self._target.create_symbol(name))
		else:
			return pending_symbol_tree_node(self)

class pending_symbol_tree_node:
	def __init__(self, parent):
		self.parent = parent

	def __set_name__(self, target, name):
		setattr(target, name, symbol_tree_node(self.parent._target.create_symbol(name)))


def register_symbol(name):
	return symbol_tree_node(SYMBOL_TREE.create_symbol(name))

def register_multiple_symbols(*name_list):
	return tuple(symbol_tree_node(SYMBOL_TREE.create_symbol(name)) for name in name_list)

def create_symbol(name):
	return SYMBOL_TREE.create_symbol(name)

SYMBOL_TREE = symbol_node(name='symbol')
symbol = symbol_tree_node(SYMBOL_TREE)
