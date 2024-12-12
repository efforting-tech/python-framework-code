from ..core import record as R
from ..symbol_factory import Local_Symbol

from . import bootstrap as MB

#FROM_CALLING_FRAME = Local_Symbol('FROM_CALLING_FRAME')

	# if module is FROM_CALLING_FRAME:
	# 	calling_frame = sys._getframe(1)
	# 	module = calling_frame.f_globals['__name__']


#TODO - default module should be FROM_CALLING_FRAME which should be a symbol
def implement_node_tree_iteratively(item, bases=(R.Record,), module=None):
	match item:
		case [*sub_items] | MB.simple_ast_node_tree(sub_items):
			for si in sub_items:
				yield from implement_node_tree_iteratively(si, bases, module)

		case MB.simple_ast_type(name, members, children):
			new_type = type(name, bases, dict(
				__annotations__ = {member_name: R.Field(default=None) for member_name in members or ()},
				__module__ = module,
			))

			yield new_type.__name__, new_type
			for child in children:
				yield from implement_node_tree_iteratively(child, (new_type,), module)

		case MB.simple_ast_symbols(members):
			for m in members:
				yield m.name, Local_Symbol(m.name)

		case symbol if symbol is None:
			pass

		case unhandled:
			raise Exception(unhandled)

