import re
from .. import record as R
from ... import Symbol as S
from . import aggregation as AGR

from ..decoration import Pending_Decorator

from .rules import LUT_Rule, Regex_Rule, Generic_Rule

class id_key(R.Record):
	target: R.Field()

	def __hash__(self):
		return object.__hash__(self.target)#id(self.target)

	def __eq__(self, other):
		match other:
			case id_key(other_target):
				return self.target is other_target

			case _:
				return self.target is other


class Rule_Match(R.Record):
	rule: R.Field()
	item: R.Field()
	match: R.Field()


class Regulations(R.Record):
	rules: R.Field(factory=list)
	fallback_rule: R.Field() = None

	def copy(self):
		return type(self)(rules=type(self.rules)(self.rules), fallback_rule=self.fallback_rule)

	def extend(self, updates):
		self.rules.extend(updates.rules)

	def register_function(self, condition):
		def finalize(function):
			self.rules.append(Generic_Rule(condition, function))
			return function

		return Pending_Decorator(finalize)

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

	def extend(self, updates):
		self.rules.update(updates.rules)

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

class Reducing_Type_LUT_Regulations(LUT_Regulations):
	LUT_key: R.Field() = staticmethod(lambda t: (type(t[0]), type(t[1])))

	def register_function(self, left_condition, right_condition):
		return super().register_function((left_condition, right_condition))


class ID_LUT_Regulations(LUT_Regulations):
	LUT_key: R.Field() = id_key


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

	def create_child(self, updates):
		result = type(self)(regulations=self.regulations.copy())
		#TODO - deal with fallback regulations - we should have methods to perform reasonable deltas here
		#TODO improve this API
		result.regulations.extend(updates.regulations)
		return result

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

	def bound_dispatch_sequence(self, target, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.bound_dispatch_item(target, sub_item))

		return result_aggregator

class Dispatcher(Core_Dispatcher):
	regulations: R.Field_Update(factory=Regulations)

#TODO - we should probably construct all these variants using a lazy factory system
class Type_LUT_Dispatcher(Core_Dispatcher):
	regulations: R.Field_Update(factory=Type_LUT_Regulations)

class ID_LUT_Dispatcher(Core_Dispatcher):
	regulations: R.Field_Update(factory=ID_LUT_Regulations)

class LUT_Dispatcher(Core_Dispatcher):
	regulations: R.Field_Update(factory=LUT_Regulations)


class Type_LUT_Translator(Type_LUT_Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.rule.action(item)

	#TODO - this pattern is probably common - maybe a processing-interface?
	def bound_dispatch_item(self, target, item):
		return super().dispatch_item(item).value.rule.action(target, item)


class Type_LUT_Processor(Type_LUT_Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.rule.action(item)

	#TODO - this pattern is probably common - maybe a processing-interface?
	def bound_dispatch_item(self, target, item):
		return super().dispatch_item(item).value.rule.action(target, item)

class ID_LUT_Processor(ID_LUT_Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.rule.action(item)

	#TODO - this pattern is probably common - maybe a processing-interface?
	def bound_dispatch_item(self, target, item):
		return super().dispatch_item(item).value.rule.action(target, item)


class Translator(Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.rule.action(item)


class Single_Operation_Processor(Dispatcher):
	def bound_dispatch_item(self, target, item):
		return super().dispatch_item(item).value.rule.action(target, item)

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


class Regex_Translator(Translator):
	regulations: R.Field_Update(factory=Regex_Regulations)

	def dispatch_item(self, item):
		#TODO - should we call core_dispatcher here explicitly or should we do the class hiearchy different?
		match = Core_Dispatcher.dispatch_item(self, item).value
		re_match = match.match

		named_idx = set(re_match.re.groupindex.values())
		pos = list()
		for index, value in enumerate(re_match.groups(), 1):
			if index in named_idx:
				continue
			pos.append(value)



		return match.rule.action(*pos, **re_match.groupdict())


	def bound_dispatch_item(self, target, item):
		match = Core_Dispatcher.dispatch_item(self, item).value
		re_match = match.match

		named_idx = set(re_match.re.groupindex.values())
		pos = list()
		for index, value in enumerate(re_match.groups(), 1):
			if index in named_idx:
				continue
			pos.append(value)

		return match.rule.action(target, *pos, **re_match.groupdict())



class Type_LUT_Reducer(Translator):
	regulations: R.Field_Update(factory=Reducing_Type_LUT_Regulations)

	def reduce_sequence(self, sequence):
		result = list()
		for item in sequence:
			result.append(item)

			if len(result) >= 2:
				left, right = result[-2:]

				success, sub_result = self.dispatch_pair(left, right)

				if success:
					result.pop(-1)
					result[-1] = sub_result
				else:
					pass

		if len(result) == 0:
			return None
		elif len(result) == 1:
			return result[0]
		else:
			return result

	def dispatch_pair(self, left, right):
		match_aggregator = self.item_aggregator_type()
		self.regulations.aggregate_matches(match_aggregator, (left, right))

		if match_aggregator.value != S.Not_Set:
			return True, match_aggregator.value.rule.action(left, right)

		else:
			return False, None




	def reduce(self, left, right):
		state, result = self.dispatch_pair(left, right)
		assert state, f'No reducer for {(type(left), type(right))}.'
		return result