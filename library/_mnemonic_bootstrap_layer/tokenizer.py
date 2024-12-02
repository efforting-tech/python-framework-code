from ..core.text.tokenization import Tokenization_Specifier, A
from ..core.text.tokenization.factory import MVP_Tokenizer_Factory
from ..core import record as R

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