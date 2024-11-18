
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
		fields = result.value.match.groupdict()

		def create_ast():
			for f_name, f_val in tuple(fields.items()):
				if field_processor := self.description.process_fields.get(f_name):
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

	# def register_ast_node_by_pattern(self, pattern):
	# 	tokens = self.tokenizer.tokenize(pattern).tokens
	# 	ast_node_name = translate_tokens_to_identifier(tokens)
	# 	capture_names = translate_tokens_to_captures(tokens)

	# 	print(capture_names)


	# def register_ast_node(self, pattern, ast_node, body=LA.Requires_Empty):
	# 	tokens = self.tokenizer.tokenize(pattern).tokens
	# 	regex = re.compile(translate_tokens_to_regex(tokens), re.I)

	# 	if isinstance(ast_node, str):
	# 		ast_node = self.ast_directory[ast_node]


	# 	print(regex, ast_node, body)

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

F = Tree_Processor_Factory()

main = F.create_processor('main')
categorized_project = F.create_processor('categorized_project')

# There are a few different situations here
# For instance, a common one is how Note works
# This one could potentially have some text associated with it
# The body would also be used

# This means we should not define our AST nodes based on a pattern
# A pattern can not describe the possible AST nodes we would want.

F.create_simple_ast_node('goal', 'title', 'body')

categorized_project.register(Node_Handler_Description(
	pattern = 'Goal[:][{text as title}]',
	ast = 'goal',
	body = LA.Store_Node_As('body'),
	process_fields = dict(
		title = str.strip,
	),
))



F.create_simple_ast_node('note', 'title', 'body')
F.create_simple_ast_node('categorized_project', 'category', 'title', 'contents')
F.create_simple_ast_symbol('meta_commentary')

main.register(Node_Handler_Description(
	pattern = 'Note[:][{text as title}]',
	ast = 'note',
	body = LA.Store_Node_As('body'),
	process_fields = dict(
		title = str.strip,
	),
))

main.register(Node_Handler_Description(
	pattern = 'Meta Commentary[:]',
	ast = 'meta_commentary',
))


main.register(Node_Handler_Description(
	pattern = 'Define {name as category} Project[:][{text as title}]',
	ast = 'categorized_project',
	body = LA.Store_Node_As('contents', processor=categorized_project),
	process_fields = dict(
		title = str.strip,
	),
))



r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	meta commentary:
	note: Here is a note
		With a bunch of
		body stuff

	define crazy project: The big rabbit
		Goal: do some stuff



'''))



print(r.value)

exit()



examples = list_from_lines_with_content('''

	Define {name as category} Project[:]
	Sketch[:] {text}
	Explanation for {name}[:]
	Language[:] {text}
	Directory[:] {text}
	Attachments[:]

''')

for item in examples:
	print(item)
	main.register_ast_node_by_pattern(item)
	print()


# def translate_tokens_to_structure(item):
# 	match item:
# 		case list():
# 			return list(map(translate_tokens_to_structure, item))

# 		case Word() | Text() | Whitespace():
# 			return type(item)

# 		case Optional(value) | Expression(value):
# 			return type(item)(translate_tokens_to_structure(value))

# 		case unmatched:
# 			raise Exception(unmatched)


# for item in examples:
# 	print(item)
# 	print(translate_tokens_to_structure( main_tokenizer.tokenize(item).tokens ))
# 	print()


