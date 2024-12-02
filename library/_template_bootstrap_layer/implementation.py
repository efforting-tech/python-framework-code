from .records import F_AST, N_AST
from . import tokenizer as MT
import re


def iteratively_implement_title(context, parent, item):
	match item:
		case [*list_of_items]:
			for sub_item in list_of_items:
				yield from iteratively_implement_title(context, parent, sub_item)

		case MT.Raw_Expression(rex):
			yield context.compile_expression(parent, rex.group(0))

		case MT.Text(re.Match() as match):
			yield match.group()

		case unmatched:
			raise Exception(type(item))

	yield from ()

#We might use a "manual" dispatcher here (match statement)
def iteratively_implement_template(context, item):
	match item:
		case [*list_of_items]:
			for sub_item in list_of_items:
				yield from iteratively_implement_template(context, sub_item)

		case F_AST.node(source, title, body):
			n_title = tuple(iteratively_implement_title(context, item, title))
			n_body = tuple(iteratively_implement_template(context, body))
			yield N_AST.node(item, n_title, n_body)

		case F_AST.statement(source, title, body):
			match tuple(iteratively_implement_title(context, item, title)):
				case [str(title_text)]:
					#print('STATEMENT TEXT', title_text)
					yield context.compile_statement(item, title_text, body)

				case [*list_of_items]:
					#One thing to consider here is that if the expression evaluates to a non indirect statement this statement could be treated like a direct one.
					#But we may still opt to not do that in order to allow it to be interpreted differently at some future point in a different context.
					#I guess this could be controlled by the context - we could have an optional optimization function we could call.
					yield N_AST.indirect_statement(item, list_of_items, body)

				case unmatched:
					raise Exception(unmatched)

		case unmatched:
			raise Exception(type(item))

