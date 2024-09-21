from .. import Strict_Symbol as SS

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
			return SS.Empty		#NOTE: If we were to return symbol.no_value we get an exception due to data descriptor failure
			#TODO - this and similar notes should be compiled into the documentation so that we can warn about it in the relevant places - possibly also have a section of recommended code models

	def stack(self, value):
		return Single_Value_Stack_Frame(self, value)

	def get(self, default=None):
		if len(self):
			return self[-1]
		else:
			return default

	def pop(self, default=SS.Action.Raise_Exception):
		if len(self):
			return super().pop(-1)
		elif default is SS.Action.Raise_Exception:
			raise Exception('pop from empty stack')	#TODO improve message
		else:
			return default

