class Identifier_Tree_Reference:
	def __init__(self, _target, _create_new=False):
		self._target = _target
		self._create_new = _create_new
		self._cache = dict()

	def __eq__(self, other):
		match other:
			case Identifier_Tree_Reference():
				return self._target == other._target
			case Identifier_Tree():
				return self._target == other

		return False

	def __hash__(self):
		return hash(self._target)

	def __dir__(self):
		return self._target.children.keys()

	def __repr__(self):
		return f'{type(self).__qualname__}({self._target.path!r})'

	def __getattr__(self, name):
		if self._create_new:
			if cached := self._cache.get(name):
				return cached
			else:
				child = self._target.get_or_create(name)
				child_ref = self._cache[name] = child.get_reference(True)
				return child_ref
		else:
			if child := self._target.get(name):
				child_ref = self._cache[name] = child.get_reference()
				return child_ref
			else:
				raise AttributeError(f'There is no child {name!r} of {self}')

	def __contains__(self, other):
		#TODO - possibly cache this

		if isinstance(other, Identifier_Tree_Reference):
			for i in self._target.walk():
				if i is other._target:
					return True

		return False


class Identifier_Tree:
	def __init__(self, name=None, parent=None):
		self.name = name
		self.parent = parent
		self.children = dict()

	def get_reference(self, create_new=False):
		return Identifier_Tree_Reference(self, create_new)

	def get_or_create(self, name):
		if existing := self.children.get(name):
			return existing
		else:
			new = self.children[name] = type(self)(name, self)
			return new

	def get_or_create_by_path(self, path):
		ptr = self
		for piece in path.split('.'):
			ptr = ptr.get_or_create(piece)

		return ptr

	def get(self, name, default=None):
		return self.children.get(name, default)

	def walk(self):
		#Walk bredth first
		for c in self.children.values():
			yield c
			yield from c.walk()


	@property
	def path(self):
		if self.parent and self.parent.name:
			return f'{self.parent.path}.{self.name}'
		else:
			return self.name


	def __repr__(self):
		return f'{type(self).__qualname__}({self.path!r})'

