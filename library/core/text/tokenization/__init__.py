from ... import record as R
from ...symbol import Symbol
from .... import Symbol as S

#Tokenization actions - todo - put in a module
class A:
	class Enter_Tokenizer(R.Record):
		target: R.Field()
		wrapper: R.Field(default=None)
		unpack: R.Field(default=False)

	class Wrapped_Chain_Tokenizer(R.Record):
		target: R.Field()
		wrapper: R.Field()

	class Action_Sequence(R.Record):
		sequence: R.Field(kind=S.Member.Kind.All_Positional)

	class Emit(R.Record):
		value: R.Field()

	class Wrap(R.Record):
		wrapper: R.Field()

	class Wrap_Match(R.Record):
		wrapper: R.Field()

	Raise_Exception = Symbol('Raise_Exception')
	Return = Symbol('Return')


Match_Anything = Symbol('Match_Anything')


class Literal_Match(R.Record):
	value: R.Field()

class Regex_Match(R.Record):
	value: R.Field()

class Rule(R.Record):
	condition: R.Field()
	action: R.Field()


class Include_Tokenizer(R.Record):
	tokenizer: R.Field()


class Tokenization_Specifier(R.Record):
	name: R.Field()
	rules: R.Field(factory=list)
	default_action: R.Field(default=None)
	chain: R.Field(default=None)
	wrapper: R.Field(default=None)

	def register_literal_token(self, token, action):
		self.rules.append(Rule(Literal_Match(token), action))

	def register_regex_token(self, token, action):
		self.rules.append(Rule(Regex_Match(token), action))

	def include_tokenizer(self, tokenizer):
		self.rules.append(Include_Tokenizer(tokenizer))

	def register_default(self, action):
		self.default_action = action






class Tokenization_Result(R.Record):
	text: R.Field()
	start: R.Field()
	tokens: R.Field(factory=list)
	end: R.Field() = None
	finalized: R.Field() = False

	def __iter__(self):
		yield from self.tokens

	def emit(self, item):
		self.tokens.append(item)

