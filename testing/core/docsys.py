#Next thing: https://github.com/efforting-tech/python-framework-code/issues/3

from pathlib import Path
from efforting.mvp6.core.text import Immutable_Tree_View
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core import record as R
from efforting.mvp6.core.text.tokenization.factory import MVP_Tokenizer_Factory



#These are records for the things our tokenizer may encounter
class Expression(R.Record):
	value: R.Field()

class Optional(R.Record):
	value: R.Field()

class Word(R.Record):
	value: R.Field()

class Text(R.Record):
	value: R.Field()

class Whitespace(R.Record):
	value: R.Field()





#This is a specification for a tokenizer
top = Tokenization_Specifier('top')
main = Tokenization_Specifier('main')
common = Tokenization_Specifier('common')
innermost_common = Tokenization_Specifier('innermost_common')
expression = Tokenization_Specifier('expression')

main.register_literal_token(']', A.Return)
main.register_literal_token('}', A.Raise_Exception)
main.include_tokenizer(common)

common.register_literal_token('{', A.Enter_Tokenizer(expression, wrapper=Expression))
common.register_literal_token('[', A.Enter_Tokenizer(main, wrapper=Optional))

innermost_common.register_regex_token(r'\w+', A.Emit(A.Wrap(Word)))
innermost_common.register_regex_token(r'\s+', A.Emit(A.Wrap(Whitespace)))
innermost_common.register_default(A.Emit(A.Wrap(Text)))
common.include_tokenizer(innermost_common)

top.include_tokenizer(common)
top.register_literal_token('}', A.Raise_Exception)
top.register_literal_token(']', A.Raise_Exception)

expression.register_literal_token('}', A.Return)
expression.include_tokenizer(innermost_common)



main_tokenizer = MVP_Tokenizer_Factory.implement_tokenizer(top)

import re


class MEP_Capture_Data(R.Record):
	regular_expression: R.Field()
	name: R.Field() = None
	post_processor: R.Field() = None
	validator: R.Field() = None


mnemonic_expression_parser = Tree_View_Regex_Dispatcher()

@mnemonic_expression_parser.register_function(r'(?i:name\s+as\s+(\w+))')
def mep_name_as_alias(dispatcher, node, result):
	[alias] = result.value.match.groups()
	return MEP_Capture_Data(rf'(?P<{alias}>\w+)', alias)

@mnemonic_expression_parser.register_function(r'(?i:name)')
def mep_name(dispatcher, node, result):
	return MEP_Capture_Data(r'(\w+)')

@mnemonic_expression_parser.register_function(r'(?i:text)')
def mep_text(dispatcher, node, result):
	return MEP_Capture_Data(r'(.+)')

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



#HACK - this should not be a regex dispatcher but we will use that for now
class Tree_Dispatcher(Tree_View_Regex_Dispatcher):
	def register_handler(self, pattern):
		tokens = main_tokenizer.tokenize(pattern).tokens
		regex = re.compile(translate_tokens_to_regex(tokens), re.I)
		return super().register_function(regex)

d = Tree_Dispatcher()


@d.register_handler('Meta Commentary[:]')
def meta_commentary(dispatcher, node, result):
	print(result)

@d.register_handler('Define {name as category} Project[:]')
def define_project_of_category(dispatcher, node, result):
	(category,) = result.value.match.groups()
	print(category)

@d.register_handler('Sketch[:] {text}')
def define_sketch(dispatcher, node, result):
	(text,) = result.value.match.groups()
	print(text)

@d.register_handler('Note[:]')
def define_body_comment(dispatcher, node, result):
	pass

@d.register_handler('Note[:] {text}')
def define_line_and_body_comment(dispatcher, node, result):
	(text,) = result.value.match.groups()
	print(text)

@d.register_handler('Explanation for {name}[:]')
def define_explanation(dispatcher, node, result):
	(name,) = result.value.match.groups()
	print(name)

@d.register_handler('Language[:] {text}')
def define_language(dispatcher, node, result):
	(name,) = result.value.match.groups()
	print(name)

@d.register_handler('Directory[:] {text}')
def define_directory(dispatcher, node, result):
	(name,) = result.value.match.groups()
	print(name)

@d.register_handler('Attachments[:]')
def define_language(dispatcher, node, result):
	pass





d.dispatch_tree(Immutable_Tree_View.from_str(Path('/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-mvp6/planning/Template Language.tdoc').read_text()))