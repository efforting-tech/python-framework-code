import sys
from .factory_helpers import Register_Interface


def create_ABC_Node(name, parent=None, auto_graft=None):
	return ABC_Node(name, (), dict(
		_name = name,
		_parent = parent,
		_auto_graft = auto_graft,
		__module__ = parent._path if parent else 'ABC',
	))



class ABC_Node(type):
	def __contains__(self, sub_item):
		path_start = len(self._path) + 1
		choices = {s._path[path_start:]:s for s in self._iter_children(True, True)}
		if isinstance(sub_item, str):
			return sub_item in choices.keys()
		elif isinstance(sub_item, ABC_Node):
			return sub_item in choices.values()



	def _set_auto_graft_here(self, stack_adjustment=0):
		self._auto_graft = sys._getframe(stack_adjustment + 1).f_locals

	def _iter_children(self, recursive=False, leaf_only=False):
		for name in object.__dir__(self):
			if name.startswith('_'):
				continue

			child = getattr(self, name)

			if recursive:
				if not leaf_only or (leaf_only and not(tuple(child._iter_children()))):
					yield child

				yield from child._iter_children(recursive, leaf_only)

			else:
				yield child


	@property
	def _path(self):
		if self._parent:
			return f'{self._parent._path}.{self._name}'
		else:
			return self._name



def register_node(target, abc_node):
	ptr = target
	parent = None
	for piece in abc_node.split('.'):
		assert not piece.startswith('_') #TODO - proper exception
		if pending := getattr(ptr, piece, None):
			ptr = pending
		else:
			new = ABC_Node(piece, ptr)
			if ptr._auto_graft is not None:
				ptr._auto_graft[new._name] = new

			setattr(ptr, piece, new)
			ptr = new

	return ptr


interface = Register_Interface(create_ABC_Node)
register_abc_here = interface.register_entries_here
register_abc_at_target = interface.register_entries_at_target
register_abc = interface.register_entry