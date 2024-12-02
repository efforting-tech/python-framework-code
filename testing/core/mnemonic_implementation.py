from efforting.mvp6.core import record as R
from efforting.mvp6.symbol_factory import Local_Symbol


from efforting.mvp6._mnemonic_bootstrap_layer import bootstrap_processor as MB

def implement_node_tree_iteratively(item, bases=(R.Record,)):
	match item:
		case [*sub_items] | MB.simple_ast_node_tree(sub_items):
			for si in sub_items:
				yield from implement_node_tree_iteratively(si, bases)

		case MB.simple_ast_type(name, members, children):
			new_type = type(name, bases, dict(
				__annotations__ = {member_name: R.Field(default=None) for member_name in members or ()},
			))

			yield new_type.__name__, new_type
			for child in children:
				yield from implement_node_tree_iteratively(child, (new_type,))

		case MB.simple_ast_symbols(members):
			for m in members:
				yield m.name, Local_Symbol(m.name)

		case unhandled:
			raise Exception(unhandled)

