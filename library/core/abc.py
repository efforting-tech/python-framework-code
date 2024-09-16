#NOTE - we may also introduce a quasi type system where instancecheck uses a set of conditions
#NOTE - before we had that path.to.thing automatically implies path.to and path - should we do that? (update: we are doing that)

#TODO - code dedup with Symbol
class ABC_Registry:
	def __init__(self):
		self.lut_type_to_abc = dict()
		self.lut_abc_to_type = dict()
		self.cache = set()

	def register(self, type, abc):
		if (type_set := self.lut_abc_to_type.get(abc)) is None:
			type_set = self.lut_abc_to_type[abc] = set()

		type_set.add(type)

		if (abc_set := self.lut_type_to_abc.get(type)) is None:
			abc_set = self.lut_type_to_abc[type] = set()

		abc_set.add(abc)

		cache_key = (type, abc)
		self.cache.add(cache_key)



	#NOTE - we may add features such as "check for subclass" and other more selective queries

	def check_if_abc(self, abc, type_ref):
		if isinstance(abc, ABC_Node_Reference):
			abc = abc._target

		if isinstance(type_ref, ABC_Node_Reference):
			type_ref = type_ref._target

		cache_key = (type_ref, abc)
		if cache_key in self.cache:
			return True

		if isinstance(type_ref, ABC_Node):
			return type_ref is abc or type_ref in abc
		else:

			for b in type.mro(type_ref):
				if b in self.lut_abc_to_type.get(abc, ()):
					self.cache.add(cache_key)
					return True

			#Check derived
			for c in abc.walk():

				if (type_ref, c) in self.cache:
					self.cache.add(cache_key)
					return True

				#TODO - check if we do type_ref.mro() somewhere else (especially disguised as type.mro()
				for b in type.mro(type_ref):
					if b in self.lut_abc_to_type.get(c, ()):
						self.cache.add(cache_key)
						return True

		return False

ABC_REGISTRY = ABC_Registry()

class ABC_Node:
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

	def __instancecheck__(self, instance):
		return ABC_REGISTRY.check_if_abc(self, type(instance))

	def __subclasscheck__(self, cls):
		return ABC_REGISTRY.check_if_abc(self, cls)


	def __call__(self, target):	#Used as decorator to register ABC
		ABC_REGISTRY.register(target, self)
		return target

	def __repr__(self):
		return f'{type(self).__qualname__}({self.path!r})'

	def __contains__(self, other):
		#TODO - possibly cache this
		for i in self.walk():
			if i is other:
				return True

		return False


class ABC_Node_Reference:
	def __init__(self, _target, _create_new=False):
		self._target = _target
		self._create_new = _create_new

	def __instancecheck__(self, instance):
		return ABC_REGISTRY.check_if_abc(self._target, type(instance))

	def __subclasscheck__(self, cls):
		return ABC_REGISTRY.check_if_abc(self._target, cls)

	def __hash__(self):
		return hash(self._target)

	def __eq__(self, other):
		if isinstance(other, type(self)):
			return self._target == other._target
		else:
			return self._target == other

	def __call__(self, target):	#Used as decorator to register ABC
		ABC_REGISTRY.register(target, self._target)
		return target

	def __repr__(self):
		return f'{type(self).__qualname__}({self._target.path!r})'

	def __getattr__(self, name):
		if self._create_new:
			child = self._target.get_or_create(name)
			return type(self)(child, True)
		else:
			if child := self._target.get(name):
				return type(self)(child)
			else:
				raise AttributeError(f'There is no child {name!r} of {self}')

	def __contains__(self, other):
		#TODO - possibly cache this
		for i in self._target.walk():
			if i is other._target:
				return True

		return False



ABC_Root_Node = ABC_Node('ABC')

def register_core_abc(path):
	ptr = ABC_Root_Node

	for p in path.split('.'):
		ptr = ptr.get_or_create(p)

	return ptr


ABC = ABC_Node_Reference(ABC_Root_Node, True)