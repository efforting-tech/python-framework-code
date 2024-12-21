from ... import records as R
from ... import Symbol as S
from ...symbols import Symbol

class Enter_Tokenizer(R.Record):
	target: R.Field()
	wrapper: R.Field(default=None)
	unpack: R.Field(default=False)
	attach_ingress: R.Field() = False

class Wrapped_Chain_Tokenizer(R.Record):
	target: R.Field()
	wrapper: R.Field()

class Action_Sequence(R.Record):
	sequence: R.Field(kind=S.Member.Kind.All_Positional)

class Emit(R.Record):
	value: R.Field()

class Literal(R.Record):
	value: R.Field()

class Wrap(R.Record):
	wrapper: R.Field()

class Return(R.Record):
	attach_egress: R.Field() = False

class Wrap_Match(R.Record):
	wrapper: R.Field()
	forward_positionals: R.Field(kind=S.Member.Kind.All_Positional)
	forward_named: R.Field(kind=S.Member.Kind.All_Named)

Raise_Exception = Symbol('Raise_Exception')
