from ..symbols import register_symbol
from ..rudimentary_type_system.bases import public_base
from .. import rudimentary_type_system as RTS
from ..table_processing.table import table
#from .tokenization import yield_value, yield_matched_text, tokenizer
import ast, re

#DEPRECATED?

class CL:
	token = register_symbol('token')

	literal_match = token()
	replacement = token()
	regex = token()

class simple_priority_parser_for_regular_expressions(public_base):
	tokenizer = RTS.positional()

	@classmethod
	def from_raster(cls, raster_table):
		rules = list()
		for pattern, regex in table.from_raster(raster_table).iter_process(process_columns=('pattern', 'regex'), column_processors=dict(regex=ast.literal_eval)):
			rules.append((re.compile(re.escape(pattern)), yield_value(CL.regex, regex)))

		return cls(tokenizer(*rules, default_action=yield_matched_text(CL.literal_match)))

	def process_pattern(self, pattern):
		result = ''
		for t in self.tokenizer.tokenize(pattern):
			match t.classification:
				case CL.literal_match:
					result += re.escape(t.match)
				case CL.regex:
					result += t.match
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')
		return result


class simple_priority_replacer(public_base):
	tokenizer = RTS.positional()

	#TODO - figuer out how we can also pass on settings from higher abstraction to lower in a nice way - or maybe even provide some sort of configuration mapping system
	@classmethod
	def from_raster(cls, raster_table):
		rules = list()
		for pattern, replacement in table.from_raster(raster_table).iter_process(process_columns=('pattern', 'replacement')):
			rules.append((re.compile(re.escape(pattern)), yield_value(CL.replacement, replacement)))

		return cls(tokenizer(*rules, default_action=yield_matched_text(CL.literal_match)))

	def process_text(self, pattern):
		result = ''
		for t in self.tokenizer.tokenize(pattern):
			match t.classification:
				case CL.literal_match | CL.replacement:
					result += t.match
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')
		return result

