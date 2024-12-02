from ..core.text import Immutable_Tree_View
from .tokenizer import template_tokenizer
from .processor import template_statement_processor, inline_expression_processor

class template_implementation_context:
	def compile_expression(self, parent, expression):
		return inline_expression_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			parent = parent,
		), Immutable_Tree_View.from_str(expression))

	def compile_statement(self, source, title, body):
		statement_node = Immutable_Tree_View.from_title_and_body(title, body.normal(1))
		return template_statement_processor.dispatcher.bound_dispatch_node(dict(
			context = self,
			source = source,
		), statement_node)
