from .directory import symbol_node, symbol_attribute_access_interface

SYMBOL_TREE = symbol_node('symbol')

class symbol_tree_node(symbol_attribute_access_interface):
	def __repr__(self):
		return f'`{self._target.path}´'

	def __call__(self, name=None):
		#TODO - explain why (consider __set_name__)
		if name:
			return symbol_tree_node(self._target.create_symbol(name))
		else:
			return pending_symbol_tree_node(self)

class pending_symbol_tree_node:
	def __init__(self, parent):
		self.parent = parent

	def __set_name__(self, target, name):
		setattr(target, name, symbol_tree_node(self.parent._target.create_symbol(name)))


symbol = symbol_tree_node(SYMBOL_TREE)

def register_symbol(name, sub_type=None):
	return symbol_tree_node(SYMBOL_TREE.create_symbol(name, sub_type))

def register_multiple_symbols(*name_list):
	return tuple(symbol_tree_node(SYMBOL_TREE.create_symbol(name)) for name in name_list)

def create_symbol(name, sub_type=None):
	return SYMBOL_TREE.create_symbol(name, sub_type=None)