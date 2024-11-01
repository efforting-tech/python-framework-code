from pathlib import Path
from efforting.mvp6.core.text import Immutable_Tree_View
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core import record as R

t = Immutable_Tree_View.from_str(Path('/srv/datacore2/devilholk/Projects/efforting.tech/github/efforting-mvp6/planning/Template Language.tdoc').read_text())


#These are records for the things our tokenizer may encounter
class Expression(R.Record):
	value: R.Field()

class Optional(R.Record):
	value: R.Field()

class Literal(R.Record):
	value: R.Field()


main = Tokenization_Specifier('main')
expression = Tokenization_Specifier('expression')
optional = Tokenization_Specifier('optional')

main.register_literal_token('{', A.Enter_Tokenizer(expression))
main.register_literal_token('}', A.Raise_Exception)
main.register_literal_token('[', A.Enter_Tokenizer(optional))
main.register_literal_token(']', A.Raise_Exception)
main.register_default(A.Emit(A.Wrap(Literal)))

expression.register_literal_token('}', A.Return)
expression.register_default(A.Emit(A.Wrap(Expression)))

optional.register_literal_token(']', A.Return)
optional.register_default(A.Emit(A.Wrap(Optional)))



#Dang it - I realized we never created a method to generate this tokenizer - we should do that before we continue


class Tree_Dispatcher(Tree_View_Regex_Dispatcher):

	def register_handler(self, pattern):
		pass


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