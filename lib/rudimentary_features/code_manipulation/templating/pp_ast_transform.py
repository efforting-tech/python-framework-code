
from ....ast_utils.extended_transformer import extended_ast_node_transformer, ast
from ....text_nodes import text_node
from .pp_bases import pp_action, pp_gen_ast

class generic_transform(extended_ast_node_transformer):

	def visit_Call(self, node):
		match node.func:
			case ast.Name(id='_preprocessor_statement'):	#possibly make this constant configurable
				#We know that the args are strings so we can simply unparse them here as literals
				title, *body = map(ast.literal_eval, node.args)
				return self.process_preprocessor_statement(title, text_node(tuple(body)))

		return node



class pp_ast_transform(generic_transform):
	def __init__(self, context):
		super().__init__()
		self.context = context

	def process_preprocessor_statement(self, command, body):
		handler = self.context.eval_expression(command)
		if handler is ...:
			pass
		elif isinstance(handler, pp_action):
			handler.process_command(self, command, body)
		elif isinstance(handler, pp_gen_ast):
			return handler.render(self)
		else:
			raise Exception(handler)



class replace_names(extended_ast_node_transformer):
	def __init__(self, replacement_map):
		self.replacement_map = replacement_map

	def visit_Name(self, node):
		#TODO harmonize
		MISS = object()
		if (replace := self.replacement_map.get(node.id, MISS)) is not MISS:
			return replace
		else:
			return node
