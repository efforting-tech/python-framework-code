from .processor import Node_Handler_Description
from . import actions as MA

def register_comment_handler(target, name, prefix_pattern):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:][{{text as title}}]',
		ast = name,
		body = MA.Store_Node_As('body'),
		process_fields = dict(
			title = lambda t: t.strip() if isinstance(t, str) else None,
		),
	))



def register_terminal_text_handler(target, name, prefix_pattern, suffix_pattern='{text}', process_fields=dict()):
	#TODO - maybe make names configurable?
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:][{suffix_pattern}]',
		ast = name,
		body = MA.Store_Node_As('body'),
		process_fields = dict(
			process_fields,
			text = lambda t: t.strip() if isinstance(t, str) else None,
		),
	))



def register_terminal_handler(target, name, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
		body = MA.Store_Node_As(body_name),
	))

def register_terminal_handler2(target, name, pattern):
	target.register(Node_Handler_Description(
		pattern = f'{pattern}',
		ast = name,
	))

def register_terminal_symbol(target, name, prefix_pattern):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
	))



def register_terminal_sub_handler(target, name, processor, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
		body = MA.Store_Node_As(body_name, processor=processor),
	))

def register_identity_sub_handler(target, name, processor, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:] {{name}}',
		ast = name,
		body = MA.Store_Node_As(body_name, processor=processor),
	))
