from .. import ABC
from .. import Symbol as S
from ..core import record as R
from ..core.dispatcher.rules import Unconditional_Rule
from ..core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from ..symbol_factory import Local_Symbol

from . import actions as MA
from .expression_parser import mnemonic_expression_parser, translate_tokens_to_regex
from .tokenizer import main_tokenizer

import re

Default_Handler = Local_Symbol('Default_Handler')

class Node_Handler_Description(R.Record):
	#Note - pattern and regex are mutually exclusive but Record does not yet support this
	#TODO: Decide if we instead should use some other way (like a container) to carry the pattern.
	pattern: R.Field() = None
	regex: R.Field() = None

	ast: R.Field()
	process_fields: R.Field(factory=dict)
	additional_factories: R.Field(factory=dict)
	body: R.Field() = MA.Requires_Empty

	bound: R.Field() = False



class Abstract_Node_Handler(R.Record):
	description: R.Field()
	ast: R.Field()	#These should be resolved at this point
	body: R.Field()

	def process_node(self, target, dispatcher, node, result):
		if (match := result.value.match) is not S.Miss:
			fields = match.groupdict()

			if not fields and not match.groups() and isinstance(self.ast, ABC.Symbol):
				return self.ast

			field_names = tuple(self.ast._record_fields.keys())

			named_idx = set(match.re.groupindex.values())
			positional_index = 0
			for index, value in enumerate(match.groups(), 1):
				if index in named_idx:
					continue

				fields[field_names[positional_index]] = value
				positional_index += 1
		else:
			if isinstance(self.ast, ABC.Symbol):
				return self.ast

			fields = dict()

		def create_ast():
			for f_name, f_val in tuple(fields.items()):
				if (field_processor := self.description.process_fields.get(f_name)) is not None:
					fields[f_name] = field_processor(f_val)

			for f_name, f_factory in self.description.additional_factories.items():
				fields[f_name] = f_factory(dict(
					field = f_name,
					node_handler = self,
					dispatcher = dispatcher,
					node = node,
					result = result,
					target = target,
				))


			return self.ast(**fields)

		match self.body:

			case MA.Store_Node_As(name, processor=processor):
				match processor:
					case Tree_Processor_Factory(dispatcher=sub_dispatcher):
						fields[name] = sub_dispatcher.dispatch_tree(node.body).value	#TODO - maybe we want to have more control here, or be more explicit

					case cb if callable(cb):
						raise NotImplementedError()

					case symbol if symbol is None:
						fields[name] = node.body

					case unhandled:
						raise Exception(unhandled)


				match self.ast:
					case type():
						return create_ast()

					case Local_Symbol():
						raise Exception()

					case unhandled:
						raise Exception(unhandled)



			case symbol if symbol is MA.Requires_Empty:
				assert not node.body.to_str().strip()
				match self.ast:
					case Local_Symbol():
						assert not fields
						return self.ast

					case type():
						return create_ast()

			case unhandled:
				raise Exception(unhandled)


class Unbound_Node_Handler(Abstract_Node_Handler):
	def __call__(self, dispatcher, node, result):
		return self.process_node(None, dispatcher, node, result)

class Bound_Node_Handler(Abstract_Node_Handler):
	def __call__(self, target, dispatcher, node, result):
		return self.process_node(target, dispatcher, node, result)

class Tree_Processor_Factory(R.Record):
	name: R.Field() = None
	ast_directory: R.Field(factory=dict)
	processor_directory: R.Field(factory=dict)
	tokenizer: R.Field() = main_tokenizer
	dispatcher: R.Field(factory=Tree_View_Regex_Dispatcher)

	def create_processor(self, name, ast_directory=None, processor_directory=None, tokenizer=None):
		result = self.processor_directory[name] = Tree_Processor_Factory(name, ast_directory or self.ast_directory, processor_directory or self.processor_directory, tokenizer or self.tokenizer)
		return result

	def register(self, handler):

		if isinstance(handler.ast, str):
			ast = self.ast_directory[handler.ast]
		else:
			ast = handler.ast

		Node_Handler = Bound_Node_Handler if handler.bound else Unbound_Node_Handler


		if bool(handler.pattern) == bool(handler.regex): # Implementation note: Fails if both or neither are defined (logical XOR).
			raise Exception(f'handler.pattern or handler.regex must be defined (mutually exclusive).')

		if handler.pattern is Default_Handler:
			self.dispatcher.register_fallback_rule(Unconditional_Rule(Node_Handler(handler, ast, handler.body)))

		elif handler.pattern:
			tokens = self.tokenizer.tokenize(handler.pattern).tokens
			regex = re.compile(translate_tokens_to_regex(tokens), re.I)
			self.dispatcher.register_function(regex)(Node_Handler(handler, ast, handler.body))
		elif regex := handler.regex:
			self.dispatcher.register_function(regex)(Node_Handler(handler, ast, handler.body))



	def create_simple_ast_symbol(self, name):
		self.ast_directory[name] = node = Local_Symbol(name)
		return node

	def create_simple_ast_node(self, name, *member_names):
		presets = {member: None for member in member_names}
		assert name not in self.ast_directory

		self.ast_directory[name] = node = type(name, (R.Record,), dict(
			**presets,
			__annotations__ = {member: R.Field() for member in member_names},
		))

		return node
