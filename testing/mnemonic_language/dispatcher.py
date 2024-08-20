# from efforting.mvp6.aggregation import First_Result, Result_List
# from efforting.mvp6.record import member as M
# from efforting.mvp6.record.base.public import Structure
from efforting.mvp6 import symbol
from efforting.mvp6.matching import data_condition as DC
from efforting.mvp6.processing.dispatcher import Regulations, Dispatcher, Mapping_Dispatcher, Categorizing_Set_Dispatcher, Transformer, Single_Operation_Processor, Sequential_Operations_Processor, generic_data_condition, Type_LUT_Regulations, LUT_Regulations

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
