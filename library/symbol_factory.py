import sys
from .factory_helpers import Register_Interface

#TODO - ABC
class Local_Symbol:
	def __init__(self, name):
		self._name = name

	def __repr__(self):
		return f'L{self._name!r}'

class Symbol:
	_REPR_PREFIX = 'S'
	def __init__(self, name, parent=None, auto_graft=None):
		self._name = name
		self._parent = parent
		self._auto_graft = auto_graft

	def __contains__(self, sub_item):
		path_start = len(self._path) + 1
		choices = {s._path[path_start:]:s for s in self._iter_children(True, False)}

		if isinstance(sub_item, str):
			return sub_item in choices.keys()
		elif isinstance(sub_item, Symbol):
			return sub_item in choices.values()



	def _set_auto_graft_here(self, stack_adjustment=0):
		self._auto_graft = sys._getframe(stack_adjustment + 1).f_locals

	def _iter_children(self, recursive=False, leaf_only=False):
		for name in super().__dir__():
			if name.startswith('_'):
				continue

			child = getattr(self, name)

			if not isinstance(child, __class__):
				continue

			if recursive:
				if not leaf_only or (leaf_only and not(tuple(child._iter_children()))):
					yield child

				yield from child._iter_children(recursive, leaf_only)

			else:
				yield child




	@property
	def _path(self):
		if self._parent and self._parent:
			return f'{self._parent._path}.{self._name}'
		else:
			return self._name

	def __repr__(self):
		def get_path(target):
			if target._parent and target._parent and target._parent._parent:	#Skip root
				return f'{get_path(target._parent)}.{target._name}'
			else:
				return target._name

		return f'{self._REPR_PREFIX}{get_path(self)!r}'


interface = Register_Interface(Symbol)
register_symbols_here = interface.register_entries_here
register_symbols_at_target = interface.register_entries_at_target
register_symbol = interface.register_entry