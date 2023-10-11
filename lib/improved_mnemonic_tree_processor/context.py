import sys

from .. import type_system as RTS
from ..type_system.bases import public_base
from ..type_system.features import classmethod_with_specified_settings
from ..symbols import register_symbol

MISS = register_symbol('internal.miss')

class context_accessor(public_base):
	_context = RTS.field()

	def __getattr__(self, key):
		if (value := self._context.get(key, MISS)) is MISS:
			raise AttributeError(f'{self} have no local or global entry {key!r}.')
		else:
			return value

	def __setattr__(self, key, value):
		self._context.locals[key] = value

	def __repr__(self):
		if self._context.name:
			return f'{self.__class__.__qualname__}({self._context.name!r})'
		else:
			return f'{self.__class__.__qualname__}({hex(id(self._context))})'





def resolve(item):
	#TODO - decide if this should be deep or not
	match item:
		case reference(target):
			return target
		case _:
			return item


class reference(public_base):
	target = RTS.positional(default=None)

class dict_interface_for_context(public_base, dict):
	#POTENTIAL TRICKY BUG - collections.abc.Mapping was not good enough for exec. This override here may not be good enough and we should make sure to properly override all methods of dict to prevent weird and hard to find bugs
	#BUG - it seems to be confirmed that unless we declare variabels as global in an expression it won't actually resolve properly
	target = RTS.positional()

	def get(self, key, default=None):
		return self.target.get(key, default)

	def clear(self):
		self.target.locals.clear()

	def copy(self):
		return dict(self.target.locals)

	def items(self):
		yield from self.target.deep_iter_items()

	def keys(self):
		yield from self.target.deep_iter()

	def pop(self, key, default=None):
		return self.target.locals.pop(key, default)

	def popitem(self):
		return self.target.locals.popitem()

	def update(self, *others, **named):
		for o in others:
			self.target.locals.update(o)

		self.target.locals.update(named)

	def values(self):
		yield from self.target.deep_iter_values()

	def __or__(self, other):
		return dict(self.target.deep_iter_items()) | other

	def __ior__(self, other):
		self.update(other)

	def __contains__(self, key):
		return self.target.contains(key)

	def __getitem__(self, key):
		return self.target.require(key)

	def __setitem__(self, key, value):
		self.target.locals[key] = value

	def __delitem__(self, key):
		del self.target.locals[key]

	def __iter__(self):
		yield from self.target.deep_iter()

	def __len__(self):
		return self.target.deep_size()

class context(public_base):
	locals = RTS.positional(factory=dict)
	name = RTS.positional(default=None, field_type=RTS.SETTING)
	parents = RTS.positional(default=())

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_this_frame(cls, stack_offset=0, *, config):
		frame = sys._getframe(stack_offset + 2)	#NOTE - +2 because decorator adds one

		if frame.f_globals is frame.f_locals:
			return cls._from_config(config, frame.f_locals)
		else:
			root = cls._from_config(config, frame.f_globals, name='root')
			return root.advanced_sub_context(frame.f_locals, config.name)

	@classmethod_with_specified_settings(RTS.SELF)	#TODO - other classmethods here
	def from_frame(cls, frame, name=None, *, config):
		root = cls._from_config(config, frame.f_globals, name='root')

		if frame.f_globals is frame.f_locals:
			return cls._from_config(config, frame.f_locals)
		else:
			return root.advanced_sub_context(frame.f_locals, name)

	def advanced_sub_context(self, locals=None, name=None):
		if locals is None:		#A problem here is that factory will not be called because locals is None, we should use the undefined-symbol instead (TODO)
			locals = dict()
		child = self.__class__(locals, name, parents=(self,))
		return child

	def sub_context(self, **updates):
		return self.__class__(updates, name=f'{self.name}/sub_context', parents=(self,))

	def get(self, key, default=None):
		if (local_value := self.locals.get(key, MISS)) is not MISS:
			return local_value

		for parent in map(resolve, self.parents):
			if (parent_value := parent.get(key, MISS)) is not MISS:
				return parent_value

		return default


	def contains(self, key):
		if key in self.locals:
			return True

		for parent in map(resolve, self.parents):
			if parent.contains(key):
				return True

		return False

	def require(self, key):
		if (local_value := self.locals.get(key, MISS)) is not MISS:
			return local_value

		for parent in map(resolve, self.parents):
			if (parent_value := parent.get(key, MISS)) is not MISS:
				return parent_value

		raise KeyError(f'{self} does not contain {key!r} in itself or any ancestor.')


	def exec(self, text):
		if isinstance(text, str):
			code = compile(text, f'<code in {self}>', 'exec')
		else:
			code = text
		g = dict_interface_for_context(self)	#This helps with the issue of lower level features "reaching in behind" to the derived dict (todo - write proper explanation)
		dict.update(g, self.deep_iter_items())
		g['__context__'] = self
		exec(code, g)

	def eval(self, text):
		if isinstance(text, str):
			code = compile(text, f'<code in {self}>', 'eval')
		else:
			code = text
		g = dict_interface_for_context(self)	#This helps with the issue of lower level features "reaching in behind" to the derived dict (todo - write proper explanation)
		dict.update(g, self.deep_iter_items())
		g['__context__'] = self
		return eval(code, g)



	def update(self, *positional, **named):
		self.locals.update(*positional, **named)

	def set(self, name, value):

		#TODO - we should have a proper resolver here where we can add new features
		if '§' in name:
			self.sub_context(__item__=value).exec(name.replace('§', '__item__'))
		else:
			self.locals[name] = value


	def deep_keys(self):
		keys = set(self.locals)
		for parent in map(resolve, self.parents):
			keys |= parent.deep_keys()
		return keys

	def deep_size(self):
		return len(self.deep_keys())

	def deep_iter(self):
		seen = set(self.locals)
		yield from self.locals

		for parent in map(resolve, self.parents):
			for key in parent.deep_iter():
				if key not in seen:
					seen.add(key)
					yield key

	def deep_iter_items(self):
		seen = set(self.locals)
		yield from self.locals.items()

		for parent in map(resolve, self.parents):
			for key, value in parent.deep_iter_items():
				if key not in seen:
					seen.add(key)
					yield key, value

	def deep_iter_values(self):
		seen = set(self.locals)
		yield from self.locals.values()

		for parent in map(resolve, self.parents):
			for key, value in parent.deep_iter_items():
				if key not in seen:
					seen.add(key)
					yield value

	@property
	def accessor(self):
		return context_accessor(self)


	def __repr__(self):
		if self.name:
			return f'{self.__class__.__qualname__}({self.name!r})'
		else:
			return f'{self.__class__.__qualname__}({hex(id(self))})'


