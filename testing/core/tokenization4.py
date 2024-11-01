#I don't remember what the tokenization2.py stuff comes from so I'll just start again here with some sort of basic runtime for creating tokenizers.
#The idea is to be able to able to create something akin to create_tokenizer in tokenization.py

from efforting.mvp6.core import record as R
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core.text.tokenization.factory import Implement_Tokenizer, Implement_Tokenizer2





#These are records for the things our tokenizer may encounter
class Expression(R.Record):
	value: R.Field()

class Optional(R.Record):
	value: R.Field()

class Literal(R.Record):
	value: R.Field()









# #This is a specification for a tokenizer
# main = Tokenization_Specifier('main')
# expression = Tokenization_Specifier('expression')
# optional = Tokenization_Specifier('optional')

# main.register_literal_token('{', A.Enter_Tokenizer(expression))
# main.register_literal_token('}', A.Raise_Exception)
# main.register_literal_token('[', A.Enter_Tokenizer(optional))
# main.register_literal_token(']', A.Raise_Exception)
# main.register_default(A.Emit(A.Wrap(Literal)))

# expression.register_literal_token('}', A.Return)
# expression.register_default(A.Emit(A.Wrap(Expression)))

# optional.register_literal_token(']', A.Return)
# optional.register_default(A.Wrapped_Chain_Tokenizer(main, Optional))


# P = Implement_Tokenizer((main, expression, optional))

# #print(P.tokenize('hello «world»!'))
# print(P.tokenize('hello [optional {thing}]!'))




# #I think we should revise the way we define our tokenizers a bit using a hierarchial method perhaps





#This is a specification for a tokenizer
top = Tokenization_Specifier('top')
main = Tokenization_Specifier('main')
common = Tokenization_Specifier('common')
expression = Tokenization_Specifier('expression')

main.register_literal_token(']', A.Return)
main.include_tokenizer(common)

common.register_literal_token('{', A.Enter_Tokenizer(expression))
common.register_literal_token('[', A.Enter_Tokenizer(main, wrapper=Optional))
common.register_default(A.Emit(A.Wrap(Literal)))

#common.include_tokenizer(top)	#NOTE - this is to test cyclic deps


top.include_tokenizer(main)
top.register_literal_token('}', A.Raise_Exception)
top.register_literal_token(']', A.Raise_Exception)

expression.register_literal_token('}', A.Return)
expression.register_default(A.Emit(A.Wrap(Expression)))


P = Implement_Tokenizer2(top)

# #print(P.tokenize('hello «world»!'))
# print(P.tokenize('hello [optional {thing}]!'))
