
def ensure_type(target, item):
	if not isinstance(item, target):
		return target(item)
	else:
		return item

	#import sys; print(f'{sys._getframe().f_code.co_name}({target!r}, {item!r})', file=sys.stderr)
	#pass

class Core_Type:
	def __instancecheck__(self, instance):
		import sys; print(f'{sys._getframe().f_code.co_name}({self!r}, {instance!r})', file=sys.stderr)

	def __subclasscheck__(self, cls):
		import sys; print(f'{sys._getframe().f_code.co_name}({self!r}, {cls!r})', file=sys.stderr)

class Core_Collection(Core_Type):
	types = (list, tuple, set, frozenset)

	def __init__(self, element=None):
		self.element = element

	def __instancecheck__(self, instance):
		#print('CHECK', self, instance)


		if not isinstance(instance, self.types):	#TODO - maybe here we should utilize the ABC system
			return False

		for e in instance:
			if not isinstance(e, self.element):
				#print('FAIL', repr(e), self.element)
				return False

		return True

	def __repr__(self):
		return f'{type(self).__qualname__}({self.element})'

	def __subclasscheck__(self, cls):
		return issubclass(cls, self.types)

	def __eq__(self, other):
		return type(self) is type(other) and self.element == other.element

	def __hash__(self):
		return hash(type(self)) ^ hash(self.element)

class Mutable_Collection(Core_Collection):
	types = (list, set)

class Immutable_Collection(Core_Collection):
	types = (tuple, frozenset)

class Sequence(Core_Collection):
	types = (list, tuple)

class Tuple(Immutable_Collection):
	types = (tuple,)

	def __call__(self, init):
		return tuple(ensure_type(self.element, e) for e in init)



class List(Mutable_Collection):
	pass
