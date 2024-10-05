import re
from .. import record as R
from ... import Strict_Symbol as S
from . import aggregation as AGR

from ..decoration import Pending_Decorator

from .rules import LUT_Rule, Regex_Rule

class Rule_Match(R.Record):
	rule: R.Field()
	item: R.Field()
	match: R.Field()


class Regulations(R.Record):
	rules: R.Field(factory=list)
	fallback_rule: R.Field() = None


	def aggregate_matches(self, aggregator, item):
		found = False
		for rule in self.rules:
			if not aggregator.accepting_work:
				break

			if match := rule.match(item):
				aggregator.aggregate(Rule_Match(rule, item, match))
				found = True


		if not found and self.fallback_rule:
			aggregator.aggregate(Rule_Match(self.fallback_rule, item, S.Miss))


class LUT_Regulations(Regulations):
	rules: R.Field(factory=dict)
	LUT_key: R.Field() = None

	def register_function(self, condition):
		def finalize(function):
			self.rules[condition] = function
			return function

		return Pending_Decorator(finalize)

	def aggregate_matches(self, aggregator, item):
		MISS = object()	#TODO local symbol
		if self.LUT_key:
			key = self.LUT_key(item)
		else:
			key = item

		action = self.rules.get(key, MISS)

		if action is MISS:
			if self.fallback_rule and aggregator.accepting_work:
				aggregator.aggregate(Rule_Match(self.fallback_rule, item, Symbol.Miss))
		else:
			if aggregator.accepting_work:
				aggregator.aggregate(Rule_Match(LUT_Rule(action), item, key))

class Type_LUT_Regulations(LUT_Regulations):
	LUT_key: R.Field() = type


def repr_reg_count(instance, field, info):
	if value := getattr(instance, field, None):
		return f'{field}[{len(value.rules)}]'
	else:
		return 'N/A'


def repr_qualname(instance, field, info):
	v = 'N/A'
	if value := getattr(instance, field, None):
		if v := getattr(value, '__qualname__'):
			v = f'<{v}>'

	return f'{field}={v}'



class Core_Dispatcher(R.Record):
	#TODO - default action
	regulations: R.Field(repr=repr_reg_count)
	item_aggregator_type: R.Field(repr=repr_qualname) = AGR.First_Result
	sequence_aggregator_type: R.Field(repr=repr_qualname) = AGR.Result_List

	#TODO currently positional/named are mixed order but positional should come first. This is a problem in base.public.Structure - workaround now is to supply later positionals as named during instanciation

	#TODO - we haven't figured out how to chain our dispatchers
	# def register_fallback_dispatcher(self, fallback_dispatcher):
	# 	match self.regulations.fallback_rule:
	# 		case fb if fb is None:
	# 			self.regulations.fallback_rule = Fallback_Rule([fallback_dispatcher])
	# 		case Fallback_Rule(fb_regs):
	# 			fb_regs.append(fallback_dispatcher)

	# 		case otherwise:
	# 			raise Exception(self.fallback_rule)

	#TODO - we will just add the other regulations but that is not what we should do (see above TODO)
	def register_fallback_dispatcher(self, fallback_dispatcher):
		self.regulations.rules.extend(fallback_dispatcher.regulations.rules)

	def register(self, *positional, **named):
		return self.regulations.register(*positional, **named)

	def register_function(self, *positional, **named):
		return self.regulations.register_function(*positional, **named)

	def dispatch_item(self, item):
		match_aggregator = self.item_aggregator_type()
		self.regulations.aggregate_matches(match_aggregator, item)

		if match_aggregator.value != S.Not_Set:
			return match_aggregator

		else:
			raise Exception(f'{self} could not dispatch {item!r}')

	def dispatch_sequence(self, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.dispatch_item(sub_item))

		return result_aggregator

class Dispatcher(Core_Dispatcher):
	pass

#TODO - we should probably construct all these variants using a lazy factory system
class Type_LUT_Dispatcher(Core_Dispatcher):
	regulations: R.Field_Update(factory=Type_LUT_Regulations)

class Transformer(Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.rule.action(item)


class Single_Operation_Processor(Dispatcher):
	def dispatch_sequence(self, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			v = self.dispatch_item(sub_item)
			if v is symbol.Action.Skip:
				continue
			else:
				result_aggregator.aggregate(v)

		return result_aggregator




class Regex_Regulations(Regulations):

	def register_function(self, pattern):
		def finalize(function):
			self.rules.append(Regex_Rule(re.compile(pattern), function))
			return function

		return Pending_Decorator(finalize)


class Regex_Transformer(Transformer):
	regulations: R.Field_Update(factory=Regex_Regulations)

	def dispatch_item(self, item):
		match = super().dispatch_item(item).value
		re_match = match.match

		named_idx = set(re_match.re.groupindex.values())
		pos = list()
		for index, value in enumerate(re_match.groups(), 1):
			if index in named_idx:
				continue
			pos.append(value)



		return match.rule.action(*pos, **re_match.groupdict())
