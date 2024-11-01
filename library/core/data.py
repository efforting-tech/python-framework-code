from .. import Symbol as S
from ..symbol_factory import Local_Symbol

class Data_Path:
	def __init__(self, *init_parts):
		self.parts = parts = list()

		for p in init_parts:
			#todo - further processing
			match p:
				case str():
					self.parts.extend(p.split('.'))
				case unhandled:
					raise ValueError(p)

	def __truediv__(self, other):
		return type(self)(*self.parts, other)

	def __str__(self):
		return '.'.join(self.parts)

	def __repr__(self):	#__repr__ will use the wrong separator (have not investigated why). Here is a hack to fix that.
		return f'{self.__class__.__qualname__}({str(self)!r})'

	@property
	def parent(self):
		return type(self)(*self.parts[:-1])



class Single_Value_Stack_Frame:
	def __init__(self, stack, pending_value):
		self.stack = stack
		self.pending_value = pending_value

	def __enter__(self):
		self.stack.push(self.pending_value)
		return self.pending_value

	def __exit__(self, et, ev, tb):
		self.stack.pop()

class Stack(list):
	push = list.append

	def __bool__(self):
		return True

	@property
	def is_empty(self):
		return len(self) == 0

	@property
	def value(self):
		if len(self):
			return self[-1]
		else:
			return S.Empty		#NOTE: If we were to return symbol.no_value we get an exception due to data descriptor failure
			#TODO - this and similar notes should be compiled into the documentation so that we can warn about it in the relevant places - possibly also have a section of recommended code models

	def stack(self, value):
		return Single_Value_Stack_Frame(self, value)

	def get(self, default=None):
		if len(self):
			return self[-1]
		else:
			return default

	def pop(self, default=S.Action.Raise_Exception):
		if len(self):
			return super().pop(-1)
		elif default is S.Action.Raise_Exception:
			raise Exception('pop from empty stack')	#TODO improve message
		else:
			return default


# class Context_Stack:
# 	def __init__(self, target, *updates, **named_updates):
# 		self.target = target
# 		self.updates = dict()
# 		for u in updates:
# 			self.updates.update(u)
# 		self.updates.update(named_updates)
# 		self.previous = None

# 	def __enter__(self):
# 		assert self.previous is None
# 		self.previous = tuple(getattr(self.target.locals, key, MISS) for key in self.updates)
# 		for key, value in self.updates.items():
# 			self.target.locals[key] = value

# 	def __exit__(self, et, ev, tb):
# 		for key, value in zip(self.updates, self.previous):
# 			if value is MISS:
# 				del self.target.locals[key]
# 			else:
# 				self.target.locals[key] = value


MISS = Local_Symbol('MISS')

class Data_Stack:
	def __init__(self, target, *updates, **named_updates):
		self.target = target
		self.updates = dict()
		for u in updates:
			self.updates.update(u)
		self.updates.update(named_updates)
		self.previous = None

	def __enter__(self):
		assert self.previous is None
		self.previous = tuple(getattr(self.target, key, MISS) for key in self.updates)
		for key, value in self.updates.items():
			setattr(self.target, key, value)

	def __exit__(self, et, ev, tb):
		for key, value in zip(self.updates, self.previous):
			if value is MISS:
				delattr(self.target, key)
			else:
				setattr(self.target, key, value)



class Identity_Reference:
	def __init__(self, target):
		self.target = target
		self.target_id = id(target)

	def __hash__(self):
		return self.target_id

	def __eq__(self, other):
		if isinstance(other, Identity_Reference):
			return self.target_id == other.target_id
		else:
			return self.target_id == id(other)

	def __repr__(self):
		return f'<{self.__class__.__name__} to {self.target!r}>'