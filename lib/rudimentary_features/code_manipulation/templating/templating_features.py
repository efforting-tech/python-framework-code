from ....text_nodes import text_node
from .... import rudimentary_type_system as RTS
from ....rudimentary_type_system.bases import standard_base
from ....rudimentary_type_system import factory_self_reference as fsr
from ....rudimentary_features.code_manipulation.templating import pp_structures
from ....rudimentary_features.code_manipulation.templating.pp_context import template_pp_context
from ....rudimentary_features.code_manipulation.templating.pp_ast_transform import pp_ast_transform, ast
from ..text_node_preprocessing import tn_preprocessor

#TODO - maybe we should separate the pythonic AST ones from the general text based ones
#		also note that we may support other languages as well later on so the structure should accomodate this.


#NOTE - one might want many different high level configurations and we should make it into a
#	configurable pipeline of dispatchers, transformers and filters so that expectations could be automatically matched.
#
#	Example - sometimes we may want to have a quick way to call a template in order to produce text
#		but in some other case we may want to do the same but to get the AST instead. Or maybe even compiled code

class attribute_based_high_level_accessor(standard_base):
	_context = RTS.positional()
	_config = RTS.positional()	#Note that we later on want to setup the configuration chain to locally check this but then fall back to context - that way we can create differently configured high level accessors

	def __getattr__(self, key):
		MISS = object()
		ctx = self._context
		if (target := ctx.locals.get(key, MISS)) is not MISS:
			return high_level_accessor(target)

		if (target := ctx.globals.get(key, MISS)) is not MISS:
			return high_level_accessor(target)

		raise AttributeError(self, key)


#The intention here is to process a value to what an end user might expect - we should name this better
#This should of course also be a configurable rule system
def hl_process_resulting_value(item):
	if isinstance(item, pp_structures.pp_prepared_template):
		return ast.unparse(item.render(None))

	raise Exception(item)

#This is for end user interfacing of complex templating features
class high_level_accessor(standard_base):
	_target = RTS.positional()

	def __call__(self, *positional, **named):
		target = self._target
		if callable(target):
			return hl_process_resulting_value(target(*positional, **named))

		raise Exception(target)



class template_context(template_pp_context, standard_base):
	text_node_transformer = RTS.field(factory=tn_preprocessor)
	ast_node_transformer = RTS.field(**fsr, factory=pp_ast_transform)

	def code_to_intermediate_tree_node(self, source):
		if isinstance(source, str):	#TODO - text_node should have an auto constructor to accept a broad range of source objects
			source = text_node.from_text(source)

		return self.text_node_transformer.transform_tree(source)

	def intermediate_to_ast(self, intermediate_tree_node):
		return ast.parse(intermediate_tree_node.text)


	#Full pipeline
	def process_text_to_text(self, source):
		intermediate_tree_node = self.code_to_intermediate_tree_node(source)
		intermediate_ast = self.intermediate_to_ast(intermediate_tree_node)
		resulting_ast = self.ast_node_transformer.visit(intermediate_ast)
		ast.fix_missing_locations(resulting_ast)
		return ast.unparse(resulting_ast)

	def get_attribute_based_high_level_accessor(self, **configuration):
		return attribute_based_high_level_accessor(self, configuration)


# def proces(code, context=None, text_node_transformer=None):


# 	#Setup preprocessor and context
# 	if not text_node_transformer:
# 		text_node_transformer = tn_preprocessor()

# 	#Stage 1 transformation from source into custom commands
# 	transformed_text = text_node_transformer.transform_tree(code).text
# 	#Stage 2 parse ast
# 	return ast.parse(transformed_text)


# # 	pp_result = pp_ast_transform(context).visit(template)
# # 	#Stage 3 - fixing locations, unparsing
# # 	ast.fix_missing_locations(pp_result)
# # print(ast.unparse(pp_result))
# # print()
# # print(compile(pp_result, '<file>', 'exec'))
