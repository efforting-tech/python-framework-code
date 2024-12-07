from ..core import record as R
from ..core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from ..core.text import Immutable_Tree_View
from ..data_utils import flatten_if_present

from .tokenizer import Word, Text, Whitespace, Optional, Expression

import re


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


@mnemonic_expression_parser.register_function(r'(?i:anything)')
def mep_anything(dispatcher, node, result):
	return MEP_Capture_Data(r'(.*)', 'anything', 'anything')

@mnemonic_expression_parser.register_function(r'(?i:anything\s+as\s+(\w+))')
def mep_anything_as_alias(dispatcher, node, result):
	[alias] = result.value.match.groups()
	return MEP_Capture_Data(rf'(?P<{alias}>.*)', 'anything', alias)





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

