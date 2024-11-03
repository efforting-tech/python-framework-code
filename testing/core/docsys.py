from pathlib import Path
from efforting.mvp6.core.text import Immutable_Tree_View
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core import record as R
from efforting.mvp6.core.text.tokenization.factory import MVP_Tokenizer_Factory

t = Immutable_Tree_View.from_str(Path('/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-mvp6/planning/Template Language.tdoc').read_text())


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


class Tree_Dispatcher(Tree_View_Regex_Dispatcher):

	def register_handler(self, pattern):
		print(main_tokenizer.tokenize(pattern).tokens)


d = Tree_Dispatcher()


#@d.register_function(r'(?i:meta\s+commentary:?)')
d.register_handler('Meta Commentary[:]')
def meta_commentary(dispatcher, node, result):
	#print(dispatcher, text, match)
	print(result)

#@d.register_function(r'(?i:define\s+software\s+project:?)')
d.register_handler('Define {name as category} Project[:]')
def def_sw_p(dispatcher, node, result):
	#print(dispatcher, text, match)
	(category,) = result.value.match.groups()
	print(category)

#@d.register_function(r'(?i:sketch:?\s*(.*))')
d.register_handler('Sketch[:] {name}')
def def_sw_p(dispatcher, node, result):
	(name,) = result.value.match.groups()
	print(name)


# @d.register_function(r'(?i:meta\s+commentary:?)')
# def meta_commentary(dispatcher, node, result):
# 	#print(dispatcher, text, match)
# 	print(result)

# @d.register_function(r'(?i:define\s+software\s+project:?)')
# def def_sw_p(dispatcher, node, result):
# 	#print(dispatcher, text, match)
# 	print(result)

# @d.register_function(r'(?i:sketch:?\s*(.*))')
# def def_sw_p(dispatcher, node, result):
# 	#print(dispatcher, text, match)
# 	print(result.value.match.groups())



#d.dispatch_tree(t)