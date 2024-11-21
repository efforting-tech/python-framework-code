#This is based on matcher_factory_test2.py
#The idea here is ultimately to be able to quickly define mnemonic processing systems but since one of the requirements are to separate AST definition from implementation
#I am going to explore some MVP implementations of
# ☑ Simple records
# ☐ Mnemonic to AST translation - still not sure we really need this as an initial step - it is currently fairly easy to define the rules if we also define some helper functions like we do
# ☐ Simple type LUT processor ← We are here
# ☐ Combination of mnemonic AST translation and LUT processor into full mnemonic solution

from efforting.mvp6.core import record as R
from efforting.mvp6.symbol_factory import Local_Symbol
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Regex_Dispatcher, Tree_View_Dispatcher

from efforting.mvp6.core.text import Immutable_Tree_View, Mutable_Tree_View
from efforting.mvp6.template_system.introspection import Dumper

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

		#TODO - use ABC for symbol
		if not fields and not match.groups() and isinstance(self.ast, Local_Symbol):
			return self.ast

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



def register_terminal_text_handler(target, name, prefix_pattern, suffix_pattern='{text}', process_fields=dict()):
	#TODO - maybe make names configurable?
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:][{suffix_pattern}]',
		ast = name,
		body = LA.Store_Node_As('body'),
		process_fields = dict(
			process_fields,
			text = lambda t: t.strip() if isinstance(t, str) else None,
		),
	))



def register_terminal_handler(target, name, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
		body = LA.Store_Node_As(body_name),
	))

def register_terminal_handler2(target, name, pattern):
	target.register(Node_Handler_Description(
		pattern = f'{pattern}',
		ast = name,
	))

def register_terminal_symbol(target, name, prefix_pattern):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
	))



def register_terminal_sub_handler(target, name, processor, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:]',
		ast = name,
		body = LA.Store_Node_As(body_name, processor=processor),
	))

def register_identity_sub_handler(target, name, processor, prefix_pattern, body_name='body'):
	target.register(Node_Handler_Description(
		pattern = f'{prefix_pattern}[:] {{name}}',
		ast = name,
		body = LA.Store_Node_As(body_name, processor=processor),
	))


def csloi(text): #Comma separated list of identifiers
	return tuple(filter(bool, map(str.strip, text.split(','))))

#Bootstrap factory

BSF = Tree_Processor_Factory()
processor_def = BSF.create_processor('processor_def')
simple_ast_node_processor = BSF.create_processor('simple_ast_node_processor')
simple_symbol_processor = BSF.create_processor('simple_symbol_processor')


simple_ast_node_tree = BSF.create_simple_ast_node('simple_ast_node_tree', 'members')
simple_ast_type = BSF.create_simple_ast_node('simple_ast_type', 'name', 'members', 'children')
simple_ast_symbols = BSF.create_simple_ast_node('simple_ast_symbols', 'members')
symbol = BSF.create_simple_ast_node('symbol', 'name')


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


simple_symbol_processor.register(Node_Handler_Description(
	pattern = '{name}',
	ast = symbol,
))

register_terminal_sub_handler(processor_def, simple_ast_node_tree, simple_ast_node_processor, 'Create Simple AST Node Tree', body_name='members')
register_terminal_sub_handler(processor_def, simple_ast_symbols, simple_symbol_processor, 'Create Symbols', body_name='members')


r = processor_def.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	create simple ast node tree:
		abstract_note: title, body
			note
			meta_comment

		abstract_regulations: name, rules
			mnemonic_regulations
			python_based_type_lut_dispatcher

		abstract_rule: pattern, body
			mnemonic_rule
			regex_rule
			literal_rule
			python_based_type_lut_dispatcher_rule: item_name
			python_based_type_lut_dispatcher_rule_without_argument

		add_argument: name, alias

		abstract_code_body: body
			unmatched_rule
			ingress
			egress

	create symbols:
		clear_arguments

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

			yield new_type.__name__, new_type
			for child in children:
				yield from implement_node_tree_iteratively(child, (new_type,))

		case simple_ast_symbols(members):
			for m in members:
				yield m.name, Local_Symbol(m.name)

		case unhandled:
			raise Exception(unhandled)


F = Tree_Processor_Factory(ast_directory=dict(implement_node_tree_iteratively(r.value)))
main = F.create_processor('main')
mnemonic_regulations = F.create_processor('mnemonic_regulations')

register_comment_handler(main, 'note', 'Note')

register_comment_handler(main, 'meta_comment', 'Meta Commentary')
register_identity_sub_handler(main, 'mnemonic_regulations', mnemonic_regulations, 'Mnemonic Regulations', body_name='rules')

register_terminal_text_handler(mnemonic_regulations, 'mnemonic_rule', 'Mnemonic Rule', '{text as pattern}')
register_terminal_text_handler(mnemonic_regulations, 'regex_rule', 'Regex Rule', '{text as pattern}')
register_terminal_text_handler(mnemonic_regulations, 'literal_rule', 'Literal Rule', '{text as pattern}')

register_terminal_handler(mnemonic_regulations, 'unmatched_rule', 'Unmatched Rule')
register_terminal_handler(mnemonic_regulations, 'ingress', 'Ingress')
register_terminal_handler(mnemonic_regulations, 'egress', 'Egress')

python_based_type_lut_dispatcher = F.create_processor('python_based_type_lut_dispatcher')
register_identity_sub_handler(main, 'python_based_type_lut_dispatcher', python_based_type_lut_dispatcher, 'python based type lut dispatcher', body_name='rules')

register_terminal_handler(python_based_type_lut_dispatcher, 'python_based_type_lut_dispatcher_rule', '{name as pattern} as {name as item_name}')
register_terminal_handler(python_based_type_lut_dispatcher, 'python_based_type_lut_dispatcher_rule', '{name as pattern}')
register_terminal_handler(python_based_type_lut_dispatcher, 'python_based_type_lut_dispatcher_rule_without_argument', '{name as pattern} without argument')

register_terminal_handler2(python_based_type_lut_dispatcher, 'add_argument', 'add argument[:] {name} as {name as alias}')
register_terminal_handler2(python_based_type_lut_dispatcher, 'add_argument', 'add argument[:] {name}')

register_terminal_symbol(python_based_type_lut_dispatcher, 'clear_arguments', 'clear arguments')



r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	python based type lut dispatcher: test_disp1

		clear arguments
		add argument: dispatcher as self

		note:
			print('This is a note!', note)

		meta_comment as some_comment:
			print('This is a note!', some_comment)

		clear arguments
		thing without argument:
			print('This is a thing')


'''))



AST = type('AST', (type,), F.ast_directory)

class dispatcher_implementer(R.Record):
	'This particular version will create a new module we can execute'

	name_prefix: R.Field() = None
	python_code: R.Field(factory=Mutable_Tree_View)
	arguments: R.Field(factory=dict)
	function_signatures: R.Field(factory=dict)
	name: R.Field() = None


	def __call__(self, item):
		match item:
			case AST.python_based_type_lut_dispatcher(name, rule_list):
				self.name = name
				for rule in rule_list:
					self(rule)

			case AST.python_based_type_lut_dispatcher_rule(name, body, item_name):
				assert name not in self.function_signatures
				arguments = ', '.join((*self.arguments, f'{item_name or name}'))
				definition = Mutable_Tree_View.from_str(f'def {name}({arguments}):')
				definition.write(body.normal(1))
				local_arguments = self.function_signatures[name] = dict(self.arguments)
				local_arguments[name] = 'item'

				self.python_code.write_line(f'@register_custom_function(dispatcher, {local_arguments!r}, {self.name_prefix}{name})')
				self.python_code.write(definition)
				self.python_code.write_line()

			case AST.python_based_type_lut_dispatcher_rule_without_argument(name, body):
				arguments = ', '.join(self.arguments)
				definition = Mutable_Tree_View.from_str(f'def {name}({arguments}):')
				definition.write(body.normal(1))
				local_arguments = self.function_signatures[name] = dict(self.arguments)

				self.python_code.write_line(f'@register_custom_function(dispatcher, {local_arguments!r}, {self.name_prefix}{name})')
				self.python_code.write(definition)
				self.python_code.write_line()

			case AST.add_argument(name, alias):
				self.arguments[alias or name] = name


			case symbol if symbol is AST.clear_arguments:
				self.arguments.clear()


			case unhandled:
				raise Exception(unhandled)

#TODO - code below should be integrated in writer above
#TODO - this thing should be tested

DI = dispatcher_implementer('AST.')
DI(r.value[0])

print(DI.function_signatures)


module_code = Mutable_Tree_View.from_str('''
	from efforting.mvp6.core.dispatcher import Type_LUT_Dispatcher
	import sys
	class throwaway_context:
		def __enter__(self):
			self.calling_locals = sys._getframe(1).f_locals
			self.snapshot = dict(self.calling_locals)

		def __exit__(self, et, ev, tb):
			self.calling_locals.clear()
			self.calling_locals.update(self.snapshot)
''').normal()

module_code.write_line()

module_code.write_line(f'class {DI.name}(R.Record):')

module_code.write_line('\tdispatcher: R.Field(Type_LUT_Dispatcher)')


module_code.write_line('\twith throwaway_context():')
module_code.write(DI.python_code, +2)


print(module_code.to_str())




# #Dumper().dump(r)	#This is a terrible dumper but will have to do

# import sys
# class throwaway_context:
# 	def __enter__(self):
# 		self.calling_locals = sys._getframe(1).f_locals
# 		self.snapshot = dict(self.calling_locals)

# 	def __exit__(self, et, ev, tb):
# 		self.calling_locals.clear()
# 		self.calling_locals.update(self.snapshot)

# #DEMO
# class test:
# 	some_list = list()

# 	with throwaway_context():
# 		def stuff():
# 			pass
# 		some_list.append(stuff)


# print(test.some_list) # [<function test.stuff at 0x76eb41663060>]
# assert not hasattr(test, 'stuff') # Assertion passes
