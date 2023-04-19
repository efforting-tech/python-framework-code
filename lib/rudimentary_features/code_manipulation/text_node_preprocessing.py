from ...text_processing.tokenization import tokenizer, yield_match, yield_classification
from ...symbols import register_symbol
from ...text_nodes import text_node
from ...data_utils import strip_sequence
from ... import type_system as RTS
from ...type_system.bases import standard_base

import re

class CL:
	token = register_symbol('preprocessor.token')

	preprocessor_statement = token()
	regular_code= token()

pp_tokenizer = tokenizer(
	(re.compile(r'^§\s*(.*)\s*$'),		yield_match(CL.preprocessor_statement)),
	default_action = 					yield_classification(CL.regular_code),
	label='pp',
)



class node_transformer_interface:
	def transform_tree(self, tree, include_blanks=True):
		lines = tuple()

		def add_lines(i):
			nonlocal lines
			if not i:
				return
			elif isinstance(i, str):
				lines += text_node.from_text(i).lines
			elif isinstance(i, (tuple, list)):
				for sub_item in i:
					add_lines(sub_item)
			else:
				lines += i.lines


		for node in tree.iter_nodes(include_blanks):
			add_lines(self.transform_node(node))


		return text_node(lines)

	#TODO - api for transform_node - maybe we define that somewhere else?


class generic_tree_node_transformer(standard_base, node_transformer_interface):
	context = RTS.optional()

	#TODO - api for transform_node - maybe we define that somewhere else?


#TODO - deprecate in favor of the custom tokenizer one?
class tn_generic_preprocessor(generic_tree_node_transformer):
	def transform_node(self, node):
		#Either it is regular code or preprocessor, not both
		if node.title:
			[token] = pp_tokenizer.tokenize(node.title)
		else:
			token = None

		#This should be a rule system later where actions can be "process sub nodes" for instance
		if token is None or token.classification is CL.regular_code:
			branches = list()
			for sub_node in node.body.iter_nodes(True):
				if transformed_node := self.transform_node(sub_node):
					branches.append(transformed_node)

			return text_node.from_title_and_branches(node.title, branches)

		elif token.classification is CL.preprocessor_statement:
			return self.handle_preprocessing_statement(token.match.group(1), node.body)



#TODO - this should be generalized to a rule system
class tn_preprocessor(tn_generic_preprocessor):
	def handle_preprocessing_statement(self, arguments, body):
		args = (arguments, *strip_sequence(body.dedented_copy().lines))
		formatted_args = ', '.join(map(repr, args))
		return text_node.from_text(f'_preprocessor_statement({formatted_args})')
