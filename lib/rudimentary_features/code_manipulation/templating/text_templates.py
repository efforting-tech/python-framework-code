from .pp_context import context
from .... import rudimentary_type_system as RTS
from ....text_processing.tokenization import tokenizer, yield_matched_text, token_match, yield_value
from ..text_node_preprocessing import tn_preprocessor
from ....text_nodes import text_node
from ....data_utils import stack
from ....rudimentary_type_system.bases import standard_base
from .template_renderer import template_renderer
from .template_classifications import CL

import re

FROM_TOKENIZER = object()	#TODO symbol

#Potentially deprecate this in favor of simple_template_renderer derivates
class pending_text_template(standard_base):
	context = RTS.positional()
	name = RTS.positional()
	body = RTS.positional()
	fields = RTS.positional()
	defaults = RTS.setting(None)	#TODO support

	def __call__(self, *positionals, **named):
		replacements = dict(zip(self.fields, positionals), **named)
		return template_renderer(self.context, self.name, replacements).transform_tree(self.body, False)

	@classmethod
	def from_text(cls, context, name, text, fields=FROM_TOKENIZER):
		body = text_node.from_text(text)
		if fields is FROM_TOKENIZER:
			fields = list()
			for item in context.tokenizer.tokenize(body.text):
				match item:
					case token_match(match=match) if item.classification is CL.expression:
						fields.append(match)

		return cls(context, name, body, fields)	#TODO support default

	@classmethod
	def from_path(cls, context, name, path, fields=FROM_TOKENIZER):
		body = text_node.from_path(path)
		if fields is FROM_TOKENIZER:
			fields = list()
			for item in context.tokenizer.tokenize(body.text):
				match item:
					case token_match(match=match) if item.classification is CL.expression:
						fields.append(match)

		return cls(context, name, body, fields)	#TODO support default


default_template_tokenizer = tokenizer(
	(re.compile(r'`(.*)´'),		yield_matched_text(CL.expression)),
	default_action = 			yield_matched_text(CL.text),
	label = 'default_template_tokenizer',
)



class default_template_processor(tn_preprocessor):
	def handle_preprocessing_statement(self, statement, body):
		#Ugly hack because I have not properly defined my APIs to carry the information I need
		with stack(globals(), ctx=self.context, processor=self, body=body.dedented_copy()):
			return self.context.eval_expression(statement)
		#print(arguments, body)



class context_accessor(standard_base):
	_target = RTS.positional()

	def __getattr__(self, key):
		try:
			return self._target.locals[key]
		except:
			raise AttributeError(self._target, key) from None

class template_context(context):
	tokenizer = RTS.setting(default_template_tokenizer)
	template_processor_type = RTS.setting(default_template_processor)
	processor = RTS.field()

	def get_context_accessor(self):
		return context_accessor(self)

	@RTS.initializer
	def init(self):
		if not getattr(self, 'processor', None):
			self.processor = self.template_processor_type(self)

	def process(self, item):
		match item:
			case str():
				return self.processor.transform_tree(text_node.from_text(item)).text.strip()
			case text_node():
				return self.processor.transform_tree(item).text.strip()

		raise ValueError(item)



	class builtins:
		def create_tree(name):
			ctx.locals[name] = body

		def create_template(name, *fields):
			ctx.locals[name] = pending_text_template(ctx, name, body, fields)

		def eval(value, **replacements):
			#This is shorthand for creating an anonymous template and render it
			return pending_text_template(ctx, 'anonymous', text_node((value, *body.lines)), ())(**replacements)





def custom_template_tokenizer(ingress, egress, *replacements, name='custom_template_tokenizer'):

	rules = list()

	i = iter(replacements)	#TODO - use consequtive chunk reader
	for find in i:
		replace = next(i)
		rules.append((re.compile(re.escape(find)), yield_value(CL.text, replace)))

	rules.append((re.compile(rf'{re.escape(ingress)}(.*?){re.escape(egress)}'),		yield_matched_text(CL.expression)))
	return tokenizer(name, *rules, default_action = yield_matched_text(CL.text))


