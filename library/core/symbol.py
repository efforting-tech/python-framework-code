SYMBOL_PARENT_LUT = dict()

class Symbol(type):
	def __new__(cls, name, *members):
		scope = dict(
			__name__ = name,
		)

		for m in members:
			scope[m.__name__] = m

		result = super().__new__(cls, name, (), scope)

		for m in members:
			SYMBOL_PARENT_LUT[m] = result

		return result

	def __contains__(self, other):
		ptr = other
		while ptr:
			if ptr is self:
				return True
			ptr = SYMBOL_PARENT_LUT.get(ptr)
		return False


	def __init__(self, *p, **n):
		pass

	def __dir__(self):
		return sorted((m.__name__ for m in self), key=str)

	def __iter__(self):
		yield from (m for m in self.__dict__.values() if isinstance(m, Symbol))

	def __str__(self):
		if parent := SYMBOL_PARENT_LUT.get(self):
			return f'{parent}.{self.__name__}'
		else:
			return self.__name__

	def __repr__(self):
		return f'«S {self}»'

class Local_Symbol(Symbol):
	def __repr__(self):
		return f'«LS {self}»'


class Enum_Choice(Symbol):
	pass

class Enum_Identity(Enum_Choice):
	def __repr__(self):
		return f'«EI {self}»'

class Enum_Value(Enum_Choice):
	def __new__(cls, name, value):
		result = super().__new__(cls, name)
		result.__value = value
		return result

	def __repr__(self):
		return f'«EV {self}: {self.__value!r}»'

	def __int__(self):
		return self.__value

class Enum(Symbol):
	def __new__(cls, name, *members, **values):
		pending_members = list()
		for m in members:
			match m:
				case str():
					pending_members.append(Enum_Identity(m))
				case unsupported:
					raise Exception(unsupported)

		for member_name, value in values.items():
			match value:
				case int():
					pending_members.append(Enum_Value(member_name, value))
				case unsupported:
					raise Exception(unsupported)



		return super().__new__(cls, name, *pending_members)

	#TODO - cache this
	def _get_reverse_value_lut(self):

		value_lut = dict()
		index_lut = dict()

		for index, value in enumerate(self):
			match value:
				case Enum_Value():
					value_lut[int(value)] = value

				case Enum_Identity():
					index_lut[index] = value

				case unhandled:
					raise TypeError(f'{value!r} is not a valid enumerator entry')


		if value_lut and not index_lut:
			return value_lut
		elif index_lut and not value_lut:
			return index_lut
		elif value_lut and index_lut:
			raise Exception(f'Enumerator {self!r} have both indices and values assigned - currently we will not reconcile that')
		else:
			return {}


	def __getitem__(self, key):
		return self._get_reverse_value_lut()[key]

	def __repr__(self):
		return f'«E {self}»'



if False:

	#NOTE - we should not use identity check with symbols because of the various references we use

	#NOTE - we may also introduce a quasi type system where instancecheck uses a set of conditions
	#NOTE - before we had that path.to.thing automatically implies path.to and path - should we do that? (update: we are doing that)

	#TODO - code dedup with ABC



	class Symbol_Node_Reference:
		def __init__(self, _target, _create_new=False):
			self._target = _target
			self._create_new = _create_new
			self._cache = dict()

		def __eq__(self, other):
			match other:
				case Symbol_Node_Reference():
					return self._target == other._target
				case Symbol_Node():
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

			if isinstance(other, Symbol_Node_Reference):
				for i in self._target.walk():
					if i is other._target:
						return True

			return False


	class Symbol_Node:
		def __init__(self, name=None, parent=None):
			self.name = name
			self.parent = parent
			self.children = dict()

		def get_reference(self, create_new=False):
			return Symbol_Node_Reference(self, create_new)

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

	Symbol_Root_Node = Symbol_Node('Symbol')

	def register_core_abc(path):
		ptr = ABC_Root_Node

		for p in path.split('.'):
			ptr = ptr.get_or_create(p)

		return ptr

	#NOTE - we should use references as the identities
	Symbol = Symbol_Root_Node.get_reference(True)
	Strict_Symbol = Symbol_Root_Node.get_reference(False)