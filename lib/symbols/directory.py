from ..type_system import field, initialization, factory_self_reference as fsr
from ..rudimentary_types.data_path import data_path
from ..data_utils.proxy import register_class_tree_proxy_resolution



class symbol_node:
	name = field(default=None)
	parent = field(default=None)
	sub_type = field(**fsr, factory=lambda s:s.__class__)

	children = field(factory=dict, positional=False)
	prefix = field(default=None, positional=False)	#TODO - consider if configuration should be marked in some way - and also look at what happens when subclass overwrite field (would be nice to handle this well and consistently)

	__init__ = initialization.standard_fields

	def create_symbol(self, path, sub_type=None):
		ptr = self
		for piece in data_path(path).parts:
			if not piece.isidentifier():
				raise ValueError(f'Path {path!r} contains non identifiers')
			if pending := ptr.children.get(piece):
				ptr = pending
			else:
				parent = ptr
				ptr = parent.children[piece] = (sub_type or self.sub_type)(piece, parent)

		return ptr

	def require_symbol(self, path):
		ptr = self
		for piece in data_path(path).parts:
			if not piece.isidentifier():
				raise Exception()
			if pending := ptr.children.get(piece):
				ptr = pending
			else:
				raise Exception()

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


#Note - this one does not automatically add symbols, read only that will raise exceptions
@register_class_tree_proxy_resolution('_target')
class symbol_attribute_access_interface:
	def __init__(self, target, sub_type=None):
		self._target = target
		self._sub_type = sub_type


	def __getattr__(self, name):
		sub_type = self._sub_type or self.__class__
		if symbol := self._target.get_symbol(name):
			return sub_type(symbol, self._sub_type)
		else:
			raise AttributeError(self, name)


	#This is so that we can use this interchangeably with the targets (this is similar to the TBI identity_reference)
	def __eq__(self, other):
		return self._target == other

	def __hash__(self):
		return hash(self._target)


