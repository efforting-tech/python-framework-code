from ....type_system.bases import standard_base
from .... import type_system as RTS
import copy
from .pp_ast_transform import replace_names
from .pp_bases import pp_gen_ast
from ....ast_utils import parse_expression

class pp_ast_template(standard_base):
	name = RTS.positional()
	replacements = RTS.positional()
	body = RTS.positional()

	def prepare(self, *values):
		assert len(self.replacements) == len(values)
		return pp_prepared_ast_template(self, values)


# class pp_text_template(standard_base):
# 	name = RTS.positional()
# 	replacements = RTS.positional()
# 	body = RTS.positional()

# 	def prepare(self, *values):
# 		assert len(self.replacements) == len(values)
# 		return pp_prepared_text_template(self, values)



# from ..text_node_preprocessing import generic_tree_node_transformer

# class text_template_renderer(generic_tree_node_transformer):
# 	def transform_node(self, node):
# 		print(node)


class pp_prepared_text_template(pp_gen_ast):
	template = RTS.positional()
	values = RTS.positional()

	def render(self, processor):
		print(self.template.body)
		print(self.values)

		print(text_template_renderer(self).transform_tree(self.template.body))
		exit()

class pp_prepared_ast_template(pp_gen_ast):
	template = RTS.positional()
	values = RTS.positional()

	def render(self, processor):	#NOTE Why processor here? should that be our API? If so , why?
		replacement_map = dict(zip(self.template.replacements, map(parse_expression, self.values)))
		#We must deep copy so we are not modifying the template
		return replace_names(replacement_map).visit(copy.deepcopy(self.template.body)).body



