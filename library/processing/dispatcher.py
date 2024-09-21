#TODO - note that this module makes a few others in this directory deprecated

from ..aggregation import First_Result, Result_List
from ..record import member as M
from ..record.base.public import Structure
from .. import Symbol
from ..matching import data_condition as DC

#TODO ABC
class regex_rule(Structure):
	pattern = M.positional()
	action = M.positional(True)

	def match(self, item):
		return self.pattern.fullmatch(item)

class unconditional_rule(Structure):
	action = M.positional(True)

	def match(self, item):
		return True

class LUT_Rule(unconditional_rule):
	pass

class sub_dispatcher_rule(Structure):
	dispatcher = M.positional()
	action = M.positional(Symbol.Action.Sub_Dispatcher)


	def match(self, item):
		return self.dispatcher.dispatch_item(item)

class generic_data_condition(Structure):
	condition = M.positional()
	action = M.positional(True)

	def match(self, item):
		#TODO - when it comes to the more advanced conditions here we must work out the pattern matching system which is currently on hold

		match self.condition:
			case DC.Type_Instance(target_type):
				return self.action if isinstance(item, target_type) else False

			case DC.All() as condition:
				for sub_condition in condition:
					if not (sub_match := type(self)(sub_condition).match(item)):
						return

				return self.action

			case DC.Sequence() as condition:
				raise NotImplementedError()


			case unhandled:
				raise Exception(self.condition)

class Rule_Match(Structure):
	rule = M.positional()
	item = M.positional()
	match = M.positional()

class Regulations(Structure):
	rules = M.positional(factory=list)
	fallback_rule = M.positional(None)

	def aggregate_matches(self, aggregator, item):
		found = False
		for rule in self.rules:
			if not aggregator.accepting_work:
				break

			if match := rule.match(item):
				aggregator.aggregate(Rule_Match(rule, item, match))
				found = True


		if not found and self.fallback_rule:
			aggregator.aggregate(Rule_Match(self.fallback_rule, item, Symbol.Miss))

class LUT_Regulations(Regulations):
	rules = M.positional(factory=dict)
	LUT_key = M.positional(None)

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
	LUT_key = M.positional(type)

class Base_Dispatcher(Structure):
	#TODO - default action
	regulations = M.positional()
	item_aggregator_type = M.named(First_Result)
	sequence_aggregator_type = M.named(Result_List)

	#TODO currently positional/named are mixed order but positional should come first. This is a problem in base.public.Structure - workaround now is to supply later positionals as named during instanciation

	def dispatch_item(self, item):
		match_aggregator = self.item_aggregator_type()
		self.regulations.aggregate_matches(match_aggregator, item)

		if match_aggregator.value is not Symbol.Not_Set:
			return match_aggregator

	def dispatch_sequence(self, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.dispatch_item(sub_item))

		return result_aggregator


class Base_Named_Dispatcher(Structure):
	name = M.positional()

class Dispatcher(Base_Dispatcher):
	pass

class Named_Dispatcher(Base_Dispatcher, Base_Named_Dispatcher): #This should ensure name is first positional (note that we must reverse bases for this to work!) - TODO - maybe make a convenience function for compositing that is more readable
	pass


class Mapping_Dispatcher(Dispatcher):
	def dispatch_sequence(self, sequence):
		return {k: v.value.match for k, v in zip(sequence, super().dispatch_sequence(sequence).value)}

class Categorizing_Set_Dispatcher(Dispatcher):
	def dispatch_sequence(self, sequence):
		result = dict()

		for i, c in zip(sequence, super().dispatch_sequence(sequence).value):
			m = c.value.match
			if (e := result.get(m, None)) is None:
				result[m] = {i}
			else:
				e.add(i)

		return result

class Transformer(Dispatcher):
	def dispatch_item(self, item):
		return super().dispatch_item(item).value.match(item)

class Single_Operation_Processor(Transformer):
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


class Sequential_Operations_Processor(Single_Operation_Processor):
	item_aggregator_type = M.named(Result_List)

	def dispatch_item(self, item):
		for rm in Dispatcher.dispatch_item(self, item).value:
			pending = rm.match(item)
			if pending is Symbol.Action.Skip:
				continue
			else:
				item = pending


		return item
