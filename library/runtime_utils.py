import sys
from .counting import counter
from . import actions as A


_recursion_tracker = counter()

class recursion_limit:
	def __init__(self, limit):
		frame = sys._getframe(1)
		self.limit = limit
		self.recursion_key = frame.f_code, frame.f_lineno

	def __enter__(self):
		if _recursion_tracker.increment(self.recursion_key) > self.limit:
			_recursion_tracker.decrement(self.recursion_key)
			raise RecursionError()

	def __exit__(self, et, ev, tb):
		_recursion_tracker.decrement(self.recursion_key)


class forward_declared_instance:
	pass

class forward_declared_type(type):
	def __new__(cls):
		return type.__new__(cls, 'pending', (), {})

	__init__ = A.ignore_call

def upgrade_forward_declared_item(target, source):
	target.__class__ = source.__class__
	target.__set_state__(source.__get_state__())
