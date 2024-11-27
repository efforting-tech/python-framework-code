from efforting.mvp6.core.text.tokenization import Tokenization_Specifier, A
from efforting.mvp6.core.text.tokenization.factory import MVP_Tokenizer_Factory
from efforting.mvp6.core import record as R


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

#TODO - escape sequence for tt_spec? ChatGPT suggests: tt_expression.register_escape_sequence('\\»', A.Emit(A.Wrap_Literal('»')))
tt_expression.register_literal_token('»', A.Return)
tt_expression.register_default(A.Emit(A.Wrap_Match(Raw_Expression)))


tt_spec.register_literal_token('»', A.Raise_Exception)
tt_spec.register_literal_token('«', A.Enter_Tokenizer(tt_expression, unpack=True))
tt_spec.register_default(A.Emit(A.Wrap_Match(Text)))

template_tokenizer = MVP_Tokenizer_Factory.implement_tokenizer(tt_spec)