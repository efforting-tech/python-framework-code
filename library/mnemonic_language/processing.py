from ..processing.text_tree import Text_Tree_Processor
from ..record import member as M
from ..record.base.public import Structure
from ..processing.structures import Regex_Rule_Set, Call_Text_Tree_Processing_Function
from ..processing.text_tree import Text_Tree_Processor_State, Text_Tree_Processor
from .. import ABC



#START OF SECTION: temporary regex processing
#TODO: we should either move or remove this
from .string_formatting_rules import string_formatter
from .. import symbol
from ..processing.generic import Type_LUT_Processor, Identity_LUT_Processor, Regex_Processor
from .structures import Mnemonic, Optional, Expression
from ..document import structures as DS
from .parser import tp
import re
T = symbol.text.token

mnemonic_to_regex = Type_LUT_Processor()
mnemonic_token_to_regex = Identity_LUT_Processor()
mnemonic_expression_to_regex = Regex_Processor()

@mnemonic_to_regex.register(str)
def mtr(processor, mnemonic):
	return processor.process_item(tp.process_text(mnemonic))

@mnemonic_to_regex.register(Mnemonic)
def mtr(processor, mnemonic):
	return ''.join(map(processor.process_item, mnemonic))



@mnemonic_token_to_regex.register(T.word)
@mnemonic_token_to_regex.register(T.literal)
def mttr(processor, token, mnemonic):
	return re.escape(mnemonic.match.group())

@mnemonic_token_to_regex.register(T.whitespace)
def mttr(processor, token, mnemonic):
	return r'\s+'


@mnemonic_to_regex.register(DS.Text_Match)
def mtr(processor, mnemonic):
	return mnemonic_token_to_regex.process_item(mnemonic.token, mnemonic)

@mnemonic_to_regex.register(Optional)
def mtr(processor, mnemonic):
	inner = processor.process_item(Mnemonic(*mnemonic))
	return rf'(?:{inner})?'

@mnemonic_to_regex.register(Expression)
def mtr(processor, mnemonic):
	#NOTE - This implementation assumes it will be a single capture
	name, pattern = mnemonic_expression_to_regex().process_item(string_formatter.process_item(Mnemonic(*mnemonic)))
	return rf'(?P<{name}>{pattern})'

@mnemonic_expression_to_regex.register(r'name')
def name(processor, mnemonic):
	return 'name', r'\w+'

@mnemonic_expression_to_regex.register(r'pattern')
def pattern(processor, mnemonic):
	return 'pattern', r'.*?'

@mnemonic_expression_to_regex.register(r'(.*?)\s+as\s+(\w+)')
def pattern(processor, mnemonic):
	pattern, alias = processor.match.groups()
	sub_name, sub_pattern = processor.process_item(pattern)
	return alias, sub_pattern

#END OF SECTION: temporary regex processing




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
		return Pending_Regex_Text_Tree_Process_Function(self, mnemonic_to_regex.process_item(mnemonic))	#TODO - this is a temporary solution until the pattern system is improved