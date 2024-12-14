from ..core.text.tree import Tree_Node
from ..symbol_factory import Local_Symbol

from . import bootstrap as MB, implementation as MI
import types


def create_records(text, name='records'):
	pending = MB.simple_ast_node_processor.dispatcher.dispatch_tree(Tree_Node.from_str(text))
	scope = dict(MI.implement_node_tree_iteratively(pending.value, module=name))

	result = types.ModuleType(name)
	result.__dict__.update(scope)
	return result
