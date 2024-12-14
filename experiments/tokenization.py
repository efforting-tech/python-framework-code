from efforting.tech.template1.core.text.tokenization import Tokenization_Specifier
from efforting.tech.template1.core.text.tokenization import actions as A
from efforting.tech.template1.core import records as R
from efforting.tech.template1.core.text.tokenization.factory import MVP_Tokenizer_Factory

#This is a good start - next session we should do the indention line thing (also see core.text)


class Abstract_Token(R.Record):
	match: R.Field()

	@property
	def value(self):
		return self.match.group(0)

class Raw_Expression(Abstract_Token):
	pass

class Text(Abstract_Token):
	pass



#This is a specification for a tokenizer
tt_spec = Tokenization_Specifier('tt_spec')
tt_expression = Tokenization_Specifier('tt_expression')
tt_escape = Tokenization_Specifier('tt_escape')

tt_escape.register_literal_token('<<==!', A.Emit('<<=='))	#TODO - we should have a way to know the original so we can recreate original text
tt_escape.register_literal_token('!==>>', A.Emit('==>>'))


#TODO - escape sequence for tt_spec? ChatGPT suggests: tt_expression.register_escape_sequence('\\»', A.Emit(A.Wrap_Literal('»')))

tt_expression.include_tokenizer(tt_escape)
tt_expression.register_literal_token('==>>', A.Return)
tt_expression.register_default(A.Emit(A.Wrap_Match(Raw_Expression)))


tt_spec.include_tokenizer(tt_escape)
tt_spec.register_literal_token('==>>', A.Raise_Exception)
tt_spec.register_literal_token('<<==', A.Enter_Tokenizer(tt_expression, unpack=True))
tt_spec.register_default(A.Emit(A.Wrap_Match(Text)))

template_tokenizer = MVP_Tokenizer_Factory.implement_tokenizer(tt_spec)

print(template_tokenizer.tokenize('''

	Hello World! Here is the <<== inline expression ==>>!
	This is a <<==! literal thing

'''))