from ..core.text.tree import Tree_Node
from .tokenizer import template_tokenizer
from .processor import template_statement_processor, inline_expression_processor

class template_implementation_context:
	def compile_expression(self, parent, expression):
		return inline_expression_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			parent = parent,
		), Tree_Node.from_str(expression))

	def compile_statement(self, source, title, body):

		#TODO - we should look these up only on the title and then pass the body as an argument instead of reconstructing a new node

		statement_node = Tree_Node.from_title_and_body(title, body.indented(normalized_indention=True))

		return template_statement_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			source = source,
		), statement_node)
