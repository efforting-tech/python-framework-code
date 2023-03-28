from ....rudimentary_features.code_manipulation.text_node_preprocessing import generic_tree_node_transformer, node_transformer_interface
from ....rudimentary_type_system.bases import public_base
from .... import rudimentary_type_system as RTS
from .template_classifications import CL
from ....text_nodes import text_node
from ....text_processing.tokenization import token_match

#This implementation does not pre-render templates - TODO: fix that
class template_renderer(generic_tree_node_transformer):
	name = RTS.positional()
	replacements = RTS.positional()

	def transform_node(self, node):
		if node.title is None:
			tokens = ()
			#tokens = None
		elif len(node.title) == 0:
			tokens = ()
		else:
			tokens = tuple(self.context.tokenizer.tokenize(node.title))


		match tokens:
			# case None:
			# 	return text_node.from_title_and_body(None, self.transform_tree(node.get_body()))
			case [token_match(classification=CL.text) as m]:
				return text_node.from_title_and_body(node.title, self.transform_tree(node.get_body(), True))
			case [token_match(classification=CL.expression) as m]:
				return self.render_expression(m.match)
			case _:
				expanded_title_parts = list()
				for t in tokens:
					match t.classification:
						case CL.text:
							expanded_title_parts.append(t.match)
						case CL.expression:
							inline_expression = self.context.eval_expression(t.match, **self.replacements)

							match inline_expression:
								case int() | float() | complex() | bool():
									expanded_title_parts.append(str(inline_expression))
								case bytes():
									expanded_title_parts.append(repr(inline_expression))
								case str(value) if '\n' not in value:
									expanded_title_parts.append(value)
								case text_node() as value if len(value.lines) == 1:
									expanded_title_parts.extend(value.lines)

								case _:
									raise ValueError(f'Expanding the expression {t.match!r} in template {self.name!r} must not return things that expands to more than one line. Got: {inline_expression!r}')
						case _:
							raise Exception()

				return text_node.from_title_and_body(''.join(expanded_title_parts), self.transform_tree(node.get_body(), False))



	def render_expression(self, expression):
		return self.context.eval_expression(expression, **self.replacements)




class simple_template_renderer(public_base, node_transformer_interface):
	name = RTS.positional()
	tokenizer = RTS.positional()

	#TODO abstract method eval_expression

	def transform_node(self, node):
		if node.title is None:
			tokens = ()
			#tokens = None
		elif len(node.title) == 0:
			tokens = ()
		else:
			tokens = tuple(self.tokenizer.tokenize(node.title))


		match tokens:
			# case None:
			# 	return text_node.from_title_and_body(None, self.transform_tree(node.get_body()))
			case [token_match(classification=CL.text) as m]:
				return text_node.from_title_and_body(node.title, self.transform_tree(node.get_body(), True))
			case [token_match(classification=CL.expression) as m]:
				return self.render_expression(m.match)
			case _:
				expanded_title_parts = list()
				for t in tokens:
					match t.classification:
						case CL.text:
							expanded_title_parts.append(t.match)
						case CL.expression:
							inline_expression = self.render_expression(t.match)

							match inline_expression:
								case int() | float() | complex() | bool():
									expanded_title_parts.append(str(inline_expression))
								case bytes():
									expanded_title_parts.append(repr(inline_expression))
								case str(value) if '\n' not in value:
									expanded_title_parts.append(value)
								case text_node() as value if len(value.lines) == 1:
									expanded_title_parts.extend(value.lines)

								case _:
									raise ValueError(f'Expanding the expression {t.match!r} in template {self.name!r} must not return things that expands to more than one line. Got: {inline_expression!r}')
						case _:
							raise Exception()

				return text_node.from_title_and_body(''.join(expanded_title_parts), self.transform_tree(node.get_body(), False))


