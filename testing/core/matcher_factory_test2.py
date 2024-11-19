
from efforting.mvp6.core import record as R
from efforting.mvp6.symbol_factory import Local_Symbol
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Regex_Dispatcher, Tree_View_Dispatcher
from efforting.mvp6.core.text import Immutable_Tree_View

import re

#TODO - move to data utils
def list_from_lines_with_content(text, strip=True):
	if strip:
		return list(filter(bool, map(str.strip, text.splitlines())))
	else:
		return list(filter(bool, text.splitlines()))


from create_tokenizer import main_tokenizer, Word, Text, Whitespace, Optional, Expression

class MEP_Capture_Data(R.Record):
	regular_expression: R.Field()
	type_name: R.Field()
	name: R.Field() = None
	post_processor: R.Field() = None
	validator: R.Field() = None


mnemonic_expression_parser = Tree_View_Regex_Dispatcher()

@mnemonic_expression_parser.register_function(r'(?i:name\s+as\s+(\w+))')
def mep_name_as_alias(dispatcher, node, result):
	[alias] = result.value.match.groups()
	return MEP_Capture_Data(rf'(?P<{alias}>\w+)', 'name', alias)

@mnemonic_expression_parser.register_function(r'(?i:name)')
def mep_name(dispatcher, node, result):
	return MEP_Capture_Data(r'(\w+)', 'name', 'name')

@mnemonic_expression_parser.register_function(r'(?i:text)')
def mep_text(dispatcher, node, result):
	return MEP_Capture_Data(r'(.+)', 'text', 'text')

@mnemonic_expression_parser.register_function(r'(?i:text\s+as\s+(\w+))')
def mep_text_as_alias(dispatcher, node, result):
	[alias] = result.value.match.groups()
	return MEP_Capture_Data(rf'(?P<{alias}>.+)', 'text', alias)



def translate_expression_tokens_to_text(item):
	match item:
		case list():
			return ''.join(map(translate_expression_tokens_to_text, item))

		case Word(value) | Text(value):
			return value

		case Whitespace(value):
			return value

		case unmatched:
			raise Exception(unmatched)


def translate_tokens_to_identifier(item):
	match item:
		case list():
			return ''.join(map(translate_tokens_to_identifier, item))

		case Word(value):
			return value.lower()

		case Optional(value):
			return translate_tokens_to_identifier(value)

		case Text():
			return ''

		case Whitespace(value):
			return '_'

		case Expression(value): 	#HACK - we will simply translate this to text and manage by a separate matcher
			#NOTE - we could cache this entire thing
			text = translate_expression_tokens_to_text(value)
			mep_values = mnemonic_expression_parser.dispatch_tree(Immutable_Tree_View.from_str(text)).value

			return '_'.join(mv.name for mv in mep_values)



		case unmatched:
			raise Exception(unmatched)


def flatten(item):
	match item:
		case list() | map():
			result = list()
			for sub_item in item:
				result.extend(flatten_if_present(sub_item))

			return result

		case otherwise:
			return [otherwise]

def flatten_if_present(item):
	return list(filter(bool, flatten(item)))


def translate_tokens_to_text(item):
	match item:
		case list():
			return ''.join(map(translate_tokens_to_text, item))

		case Word(value) | Text(value):
			return value

		case Whitespace(value):
			return value

		case unmatched:
			raise Exception(unmatched)

def translate_tokens_to_captures(item):
	match item:
		case list():
			return flatten_if_present(map(translate_tokens_to_captures, item))

		case Word() | Text() | Whitespace():
			return

		case Optional(value):
			return translate_tokens_to_captures(value)

		case Expression(value): 	#HACK - we will simply translate this to text and manage by a separate matcher
			#NOTE - we could cache this entire thing
			text = translate_expression_tokens_to_text(value)
			mep_values = mnemonic_expression_parser.dispatch_tree(Immutable_Tree_View.from_str(text)).value
			return mep_values

		case unmatched:
			raise Exception(unmatched)


def translate_tokens_to_regex(item):
	match item:
		case list():
			return ''.join(map(translate_tokens_to_regex, item))

		case Expression(value): 	#HACK - we will simply translate this to text and manage by a separate matcher
			#NOTE - we could cache this entire thing
			text = translate_tokens_to_text(value)
			mep_values = mnemonic_expression_parser.dispatch_tree(Immutable_Tree_View.from_str(text)).value
			regex = ''.join(mv.regular_expression for mv in mep_values)
			return regex


		case Word(value) | Text(value):
			return re.escape(value)

		case Whitespace(value):
			return r'\s+'

		case Optional(value):
			return rf'(?:{translate_tokens_to_regex(value)})?'

		case unmatched:
			raise Exception(unmatched)



class LA:
	class Store_Node_As(R.Record):
		name: R.Field()
		processor: R.Field() = None

	class Store_Text_As(R.Record):
		name: R.Field()

	Requires_Empty = Local_Symbol('Requires_Empty')

class Node_Handler_Description(R.Record):
	pattern: R.Field()
	ast: R.Field()
	process_fields: R.Field(factory=dict)
	body: R.Field() = LA.Requires_Empty

class Node_Handler(R.Record):
	description: R.Field()
	ast: R.Field()	#These should be resolved at this point
	body: R.Field()

	def __call__(self, dispatcher, node, result):
		match = result.value.match
		fields = match.groupdict()
		field_names = tuple(self.ast._record_fields.keys())

		named_idx = set(match.re.groupindex.values())
		positional_index = 0
		for index, value in enumerate(match.groups(), 1):
			if index in named_idx:
				continue

			fields[field_names[positional_index]] = value
			positional_index += 1


		def create_ast():
			for f_name, f_val in tuple(fields.items()):
				if (field_processor := self.description.process_fields.get(f_name)) is not None:
					fields[f_name] = field_processor(f_val)

			return self.ast(**fields)

		match self.body:

			case LA.Store_Node_As(name, processor=processor):
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


			case symbol if symbol is LA.Requires_Empty:
				assert not node.body.to_str().strip()
				match self.ast:
					case Local_Symbol():
						assert not fields
						return self.ast

					case type():
						return create_ast()

			case unhandled:
				raise Exception(unhandled)

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
		tokens = self.tokenizer.tokenize(handler.pattern).tokens
		regex = re.compile(translate_tokens_to_regex(tokens), re.I)


		if isinstance(handler.ast, str):
			ast = self.ast_directory[handler.ast]
		else:
			ast = handler.ast

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


def register_comment_handler(target, name, prefix_pattern):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:][{{text as title}}]',
		ast = name,
		body = LA.Store_Node_As('body'),
		process_fields = dict(
			title = lambda t: t.strip() if isinstance(t, str) else None,
		),
	))


def register_terminal_sub_handler(target, name, processor, prefix_pattern):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
		body = LA.Store_Node_As('members', processor=processor),
	))



def csloi(text): #Comma separated list of identifiers
	return tuple(filter(bool, map(str.strip, text.split(','))))

#Bootstrap factory

BSF = Tree_Processor_Factory()
processor_def = BSF.create_processor('processor_def')
simple_ast_node_processor = BSF.create_processor('simple_ast_node_processor')


simple_ast_node_tree = BSF.create_simple_ast_node('simple_ast_node_tree', 'members')
simple_ast_type = BSF.create_simple_ast_node('simple_ast_type', 'name', 'members', 'children')

simple_ast_node_processor.register(Node_Handler_Description(
	pattern = '{name}[:]',
	ast = simple_ast_type,
	body = LA.Store_Node_As('children', processor=simple_ast_node_processor),
	process_fields = dict(
		members = csloi,
	),
))

simple_ast_node_processor.register(Node_Handler_Description(
	pattern = '{name}[:]{text as members}',
	ast = simple_ast_type,
	body = LA.Store_Node_As('children', processor=simple_ast_node_processor),
	process_fields = dict(
		members = csloi,
	),
))


register_terminal_sub_handler(processor_def, simple_ast_node_tree, simple_ast_node_processor, 'Create Simple AST Node Tree')


r = processor_def.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	create simple ast node tree:
		abstract_note: title, body
			note
			meta_comment

'''))


def implement_node_tree_iteratively(item, bases=(R.Record,)):
	match item:
		case [*sub_items] | simple_ast_node_tree(sub_items):
			for si in sub_items:
				yield from implement_node_tree_iteratively(si, bases)

		case simple_ast_type(name, members, children):
			new_type = type(name, bases, dict(
				__annotations__ = {member_name: R.Field(default=None) for member_name in members or ()},
			))

			yield new_type
			for child in children:
				yield from implement_node_tree_iteratively(child, (new_type,))

		case unhandled:
			raise Exception(unhandled)

for i in implement_node_tree_iteratively(r.value):
	globals()[i.__name__] = i

print(note('stuff'))