#I don't remember what the tokenization2.py stuff comes from so I'll just start again here with some sort of basic runtime for creating tokenizers.
#The idea is to be able to able to create something akin to create_tokenizer in tokenization.py

from efforting.mvp6.core import record as R
from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core.text.tokenization.factory import Implement_Tokenizer





#These are records for the things our tokenizer may encounter
class Inline(R.Record):
	value: R.Field()

class Text(R.Record):
	value: R.Field()

#This is a specification for a tokenizer
main = Tokenization_Specifier('main')
inline = Tokenization_Specifier('inline')

main.register_literal_token('«', A.Enter_Tokenizer(inline))
main.register_literal_token('»', A.Raise_Exception)
main.register_default(A.Emit(A.Wrap(Text)))

inline.register_literal_token('»', A.Return)
inline.register_default(A.Emit(A.Wrap(Inline)))


tokenizers = (main, inline)

P = Implement_Tokenizer(tokenizers)

#print(P.tokenize('hello «world»!'))
print(P.tokenize('hello «World»!'))
