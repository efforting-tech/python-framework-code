#TODO - deprecate and rewrite

#START OF SECTION: temporary regex processing
#TODO: we should either move or remove this
from .string_formatting_rules import string_formatter
from .. import symbol
from ..processing.generic import Type_LUT_Processor, Identity_LUT_Processor, Regex_Processor
from . import structures as S
from ..document import structures as DS
from .parser import tp
import re
T = symbol.text.token

from ..record import member as M
from ..record.base.public import Structure, Sequence

class RF:
	@staticmethod
	def CN(name, pattern):
		return rf'(?P<{name}>{pattern})'

class Signature(Structure):
		name = M.positional()
		arguments = M.positional()


class RC:
	#TODO - we should not allow double underscore in pattern captures (unless we have a resolver that can make sure things are identical or all positional)

	#TODO - define API

	class Regex_Pattern:
		def get_compiled_pattern(self):
			return re.compile(self.get_pattern())

	class Regex(Structure, Regex_Pattern):
		pattern = M.positional()

		def get_pattern(self):
			return self.pattern

		def get_captures(self):
			return dict()	#TODO - assuming no captures but we should probably verify this when creating this record. This may be a good place to use immutable records with good caching (but then renaming a pattern becomes tricky instead)

	class Capture(Structure, Regex_Pattern):
		name = M.positional()
		inner_pattern = M.positional()

		def rename(self, new_name):
			print('Rename', self.name, 'to', new_name)
			self.name = new_name

		def unpack_match(self, match):
			print('UNPACK', match.groupdict(), match.re)
			yield match.groupdict()[self.name]

		def get_captures(self):
			return {self.name: self}

		def get_pattern(self):
			return RF.CN(self.name, self.inner_pattern)

	class Signature(Structure, Regex_Pattern):
		name = M.positional()

		def unpack_match(self, match):
			import inspect
			g = match.groupdict()
			#yield g[f'{self.name__n}']
			n, a = g[f'{self.name}__n'], g[f'{self.name}__a']
			gs = dict()

			yield Signature(n, inspect.signature(eval(f'lambda {a}: None')))

		def get_captures(self):
			return {self.name: self}

		def get_pattern(self):
			p_name, p_args = RF.CN(f'{self.name}__n', r'\w+'), RF.CN(f'{self.name}__a', r'.*')
			return rf'({p_name}\s*\({p_args}\))'


	class Optional(Structure, Regex_Pattern):
		inner = M.positional()

		def get_captures(self):
			return self.inner.get_captures()

		def get_pattern(self):
			return rf'(?:{self.inner.get_pattern()})?'

	class Pattern_Collection(Sequence, Regex_Pattern):

		def get_captures(self):
			result = dict()
			for sub_pattern in self:
				to_add = sub_pattern.get_captures()

				expected_count = len(result) + len(to_add)
				result.update(to_add)
				assert len(result) == expected_count

			return result


		def get_pattern(self):
			result = ''
			for sub_pattern in self:
				match sub_pattern:
					case str():
						result += sub_pattern
					case RC.Regex_Pattern():
						result += sub_pattern.get_pattern()
					case unhandled:
						raise Exception(f'Unhandled: {unhandled!r}')#TODO better
			return result




mnemonic_to_prepared_pattern = Type_LUT_Processor()
mnemonic_token_to_regex = Identity_LUT_Processor()
mnemonic_expression_to_regex = Regex_Processor()

@mnemonic_to_prepared_pattern.register(str)
def mtr(processor, mnemonic):
	return processor.process_item(tp.process_text(mnemonic))

@mnemonic_to_prepared_pattern.register(S.Mnemonic)
def mtr(processor, mnemonic):
	return RC.Pattern_Collection(*map(processor.process_item, mnemonic))



@mnemonic_token_to_regex.register(T.word)
@mnemonic_token_to_regex.register(T.literal)
def mttr(processor, token, mnemonic):
	return RC.Regex(re.escape(mnemonic.match.group()))

@mnemonic_token_to_regex.register(T.whitespace)
def mttr(processor, token, mnemonic):
	return RC.Regex(r'\s+')


@mnemonic_to_prepared_pattern.register(DS.Text_Match)
def mtr(processor, mnemonic):
	return mnemonic_token_to_regex.process_item(mnemonic.token, mnemonic)

@mnemonic_to_prepared_pattern.register(S.Optional)
def mtr(processor, mnemonic):
	return RC.Optional(processor.process_item(S.Mnemonic(*mnemonic)))


@mnemonic_to_prepared_pattern.register(S.Expression)
def mtr(processor, mnemonic):
	#NOTE - This implementation assumes it will be a single capture
	return mnemonic_expression_to_regex.process_item(string_formatter.process_item(S.Mnemonic(*mnemonic)))


@mnemonic_expression_to_regex.register(r'name')
def name(processor, mnemonic):
	return RC.Capture('name', r'\w+')

@mnemonic_expression_to_regex.register(r'pattern')
def pattern(processor, mnemonic):
	return RC.Capture('pattern', r'.*?')

@mnemonic_expression_to_regex.register(r'signature')
def pattern(processor, mnemonic):
	return RC.Signature('signature')

@mnemonic_expression_to_regex.register(r'(.*?)\s+as\s+(\w+)')
def pattern(processor, mnemonic):
	pattern, alias = processor.state.match.value.match.groups()	# TODO - explain
	sub_pattern = processor.process_item(pattern)
	sub_pattern.rename(alias)
	return sub_pattern

#END OF SECTION: temporary regex processing



if False:

	from ..processing.text_tree import Text_Tree_Processor
	from ..record import member as M
	from ..record.base.public import Structure
	from ..processing.structures import Regex_Rule_Set, Call_Text_Tree_Processing_Function
	from ..processing.text_tree import Text_Tree_Processor_State, Text_Tree_Processor
	from .. import ABC





	@ABC.Decorator
	class Pending_Regex_Text_Tree_Process_Function(Structure):
		owner = M.positional()
		pattern = M.positional()

		def __call__(self, function):
			self.owner.rules.map_action(self.pattern, Call_Text_Tree_Processing_Function(function))
			return function


	class Mnemonic_Text_Tree_Processor_State(Text_Tree_Processor_State):
		rule = M.positional()
		match = M.positional()

		def process_item(self, title_subject):
			#TODO - we should use the rulesystem API to get the correct rule instead (but we need to harmonize our processors and make sure we can build up all the different kinds)
			self.item = title_subject
			self.rule, self.match = self.rules.lookup_rule_and_match(title_subject)
			if self.rule is symbol.action.raise_exception:
				raise Exception(f'Failed to handle: {title_subject}')	#TODO - better error

			return self.process_action(self.rule.action)



	class Mnemonic_Text_Tree_Processor(Text_Tree_Processor):
		title_comparator = M.positional()
		title_processor = M.positional()
		rules = M.positional(factory=Regex_Rule_Set)
		STATE_TYPE = M.positional(default=Mnemonic_Text_Tree_Processor_State)



		def register_mnemonic(self, mnemonic):
			return Pending_Regex_Text_Tree_Process_Function(self, mnemonic_to_prepared_pattern.process_item(mnemonic))	#TODO - this is a temporary solution until the pattern system is improved