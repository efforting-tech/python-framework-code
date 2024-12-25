from .. import records as R, ABC
from . import template_tokenizer, split_tokens_into_lines
from .lineref import Line_Reference



#TODO - implement in some abc factory module
@ABC.Factory.Contextual
class Bound_Factory(R.Record):
	factory: R.Field()

	def __call__(self, context):
		return self.factory(context['instance'])

class Document(R.Record):
	text: R.Field(repr=False)
	tokenizer: R.Field() = template_tokenizer
	tokens: R.Field(repr=False, factory=Bound_Factory(
		lambda self: self.tokenizer.tokenize(self.text).tokens
	))
	lines: R.Field(repr=False, factory=Bound_Factory(
		lambda self: tuple(split_tokens_into_lines(self.tokens, preserve_ends=True))
	))

	def __len__(self):
		return len(self.lines)

	def __getitem__(self, index):
		l, r = self.lines[index]
		return Line_Reference(self, l, r)
