from .. import record as R
from ... import Strict_Symbol as SS
from . import aggregation as AGR

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
			aggregator.aggregate(Rule_Match(self.fallback_rule, item, Symbol.Miss))





class Core_Dispatcher(R.Record):
	#TODO - default action
	regulations: R.Field()
	item_aggregator_type: R.Field() = AGR.First_Result
	sequence_aggregator_type: R.Field() = AGR.Result_List

	#TODO currently positional/named are mixed order but positional should come first. This is a problem in base.public.Structure - workaround now is to supply later positionals as named during instanciation

	def dispatch_item(self, item):
		match_aggregator = self.item_aggregator_type()
		self.regulations.aggregate_matches(match_aggregator, item)

		if match_aggregator.value is not SS.Not_Set:
			return match_aggregator

	def dispatch_sequence(self, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.dispatch_item(sub_item))

		return result_aggregator

class Dispatcher(Core_Dispatcher):
	pass
