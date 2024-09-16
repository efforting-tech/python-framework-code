#NOTE - we may also introduce a quasi type system where instancecheck uses a set of conditions
#NOTE - before we had that path.to.thing automatically implies path.to and path - should we do that? (update: we are doing that)

class Symbol_Registry:
	def __init__(self):
		self.registry = dict()




SYMBOL_REGISTRY = Symbol_Registry()

#TODO - code dedup with ABC
class Symbol_Node:
	def __init__(self, name=None, parent=None):
		self.name = name
		self.parent = parent
		self.children = dict()

	def get_or_create(self, name):
		if existing := self.children.get(name):
			return existing
		else:
			new = self.children[name] = type(self)(name, self)
			return new

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


class Symbol_Node_Reference:
	def __init__(self, _target, _create_new=False):
		self._target = _target
		self._create_new = _create_new
		self._cache = dict()

	def __repr__(self):
		return f'{type(self).__qualname__}({self._target.path!r})'

	def __getattr__(self, name):
		if self._create_new:
			if cached := self._cache.get(name):
				return cached
			else:
				child_ref = self._cache[name] = type(self)(self._target.get_or_create(name), True)
				return child_ref
		else:
			if child := self._target.get(name):
				child_ref = self._cache[name] = type(self)(child)
				return child_ref
			else:
				raise AttributeError(f'There is no child {name!r} of {self}')

	def __contains__(self, other):
		#TODO - possibly cache this
		for i in self._target.walk():
			if i is other._target:
				return True

		return False


Symbol_Root_Node = Symbol_Node('Symbol')

def register_core_abc(path):
	ptr = ABC_Root_Node

	for p in path.split('.'):
		ptr = ptr.get_or_create(p)

	return ptr

#NOTE - we should use references as the identities
Symbol = Symbol_Node_Reference(Symbol_Root_Node, True)