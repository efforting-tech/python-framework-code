from efforting.mvp6.aggregation import First_Result, Result_List
from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Structure
from efforting.mvp6 import symbol
from efforting.mvp6.matching import data_condition as DC


class generic_data_condition(Structure):
	condition = M.positional()
	action = M.positional(True)

	def match(self, item):
		match self.condition:
			case DC.Type_Instance(target_type):
				return self.action if isinstance(item, target_type) else False

			case unhandled:
				raise Exception(self.condition)

class Rule_Match(Structure):
	rule = M.positional()
	item = M.positional()
	match = M.positional()

class Regulations(Structure):
	rules = M.positional(factory=list)

	def aggregate_matches(self, aggregator, item):
		for rule in self.rules:
			if not aggregator.accepting_work:
				break

			if match := rule.match(item):
				aggregator.aggregate(Rule_Match(rule, item, match))

class LUT_Regulations(Structure):
	rules = M.positional(factory=dict)
	LUT_key = M.positional(None)

	def aggregate_matches(self, aggregator, item):
		if self.LUT_key:
			key = self.LUT_key(item)
		else:
			key = item

		rule = self.rules[key]
		if aggregator.accepting_work:
			aggregator.aggregate(Rule_Match(None, item, rule))

class Type_LUT_Regulations(LUT_Regulations):
	LUT_key = M.positional(type)

class Dispatcher(Structure):
	#TODO - default action
	regulations = M.positional()
	item_aggregator_type = M.named(First_Result)
	sequence_aggregator_type = M.named(Result_List)

	#TODO currently positional/named are mixed order but positional should come first. This is a problem in base.public.Structure - workaround now is to supply later positionals as named during instanciation

	def dispatch_item(self, item):
		match_aggregator = self.item_aggregator_type()
		self.regulations.aggregate_matches(match_aggregator, item)

		if match_aggregator.value is not symbol.not_set:
			return match_aggregator

	def dispatch_sequence(self, sequence):
		result_aggregator = self.sequence_aggregator_type()
		for sub_item in sequence:
			if not result_aggregator.accepting_work:
				break

			result_aggregator.aggregate(self.dispatch_item(sub_item))

		return result_aggregator



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
			if v is symbol.action.skip:
				continue
			else:
				result_aggregator.aggregate(v)

		return result_aggregator


class Sequential_Operations_Processor(Single_Operation_Processor):
	item_aggregator_type = M.named(Result_List)

	def dispatch_item(self, item):
		for rm in Dispatcher.dispatch_item(self, item).value:
			pending = rm.match(item)
			if pending is symbol.action.skip:
				continue
			else:
				item = pending


		return item


#  ___  ___ __  __  ___
# |   \| __|  \/  |/ _ \
# | |) | _|| |\/| | (_) |
# |___/|___|_|  |_|\___/


data = [1, 2, 3, 'hello', 'world']



r = Regulations()
r.rules.append(generic_data_condition(DC.Type_Instance(int), 'Integer'))
r.rules.append(generic_data_condition(DC.Type_Instance(str), 'String'))

d = Dispatcher(r)
print(d.dispatch_sequence(data).value)
# [First_Result(error=None, value=…), First_Result(error=None, value=…), First_Result(error=None, value=…), First_Result(error=None, value=…), First_Result(error=None, value=…)]

d2 = Mapping_Dispatcher(r)
print(d2.dispatch_sequence(data))
# {1: 'Integer', 2: 'Integer', 3: 'Integer', 'hello': 'String', 'world': 'String'}

d3 = Categorizing_Set_Dispatcher(r)
print(d3.dispatch_sequence(data))
# {'Integer': {1, 2, 3}, 'String': {'hello', 'world'}}


def call_int(value):
	return f'INTEGER({value!r})'

def call_string(value):
	return f'STRING({value!r})'

r2 = Regulations()
r2.rules.append(generic_data_condition(DC.Type_Instance(int), call_int))
r2.rules.append(generic_data_condition(DC.Type_Instance(str), call_string))

d4 = Transformer(r2)
print(d4.dispatch_sequence(data).value)
# ['INTEGER(1)', 'INTEGER(2)', 'INTEGER(3)', "STRING('hello')", "STRING('world')"]


def call_int2(value):
	if value == 2:
		return symbol.action.skip
	return f'INTEGER({value!r})'

r3 = Regulations()
r3.rules.append(generic_data_condition(DC.Type_Instance(int), call_int2))
r3.rules.append(generic_data_condition(DC.Type_Instance(str), call_string))


d5 = Single_Operation_Processor(r3)
print(d5.dispatch_sequence(data).value)
# ['INTEGER(1)', 'INTEGER(3)', "STRING('hello')", "STRING('world')"]


r4 = Regulations(list(r2.rules))
r4.rules.insert(0, generic_data_condition(DC.Type_Instance(int), call_int2))

d6 = Sequential_Operations_Processor(r4)
print(d6.dispatch_sequence(data).value)
# ["INTEGER('INTEGER(1)')", 'INTEGER(2)', "INTEGER('INTEGER(3)')", "STRING('hello')", "STRING('world')"]



r5 = Type_LUT_Regulations()
r5.rules[int] = call_int
r5.rules[str] = call_string

d7 = Transformer(r5)
print(d7.dispatch_sequence(data).value)
