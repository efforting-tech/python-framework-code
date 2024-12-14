import sys
from .. import __package__ as root_package
from collections import defaultdict

CALLING_FRAME = object()	#Using object before we have a symbol
ABC_Registry_by_target = defaultdict(set)
ABC_Registry_by_ABC = defaultdict(set)

class ABC_Node(type):

	def __new__(cls, name, entries=(), module=CALLING_FRAME):
		scope = dict()
		if module is CALLING_FRAME:
			module = sys._getframe(1).f_globals['__name__']

		for entry in entries:
			scope[entry.__name__] = entry

		scope['__module__'] = module

		return super().__new__(cls, name, (), scope)

	def __init__(self, *pos, **named):
		pass

	def __call__(self, target):	#DECORATOR
		ABC_Registry_by_target[target].add(self)
		ABC_Registry_by_ABC[self].add(target)
		return target

	def __instancecheck__(self, target):
		return type(target) in ABC_Registry_by_ABC.get(self, ())



def A(name, *entries):
	return ABC_Node(name, entries, module='ABC')

def set_qual_names(target, path=None, skip_root=False):
	if path:
		target.__qualname__ = f'{path}.{target.__name__}'
	else:
		target.__qualname__ = target.__name__

	for child_name, child_ref in target.__dict__.items():
		if child_name.startswith('_'):
			continue

		if skip_root:
			set_qual_names(child_ref, None)
		else:
			set_qual_names(child_ref, target.__qualname__)

