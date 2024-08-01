from ..matching import data_condition as DC
from ..processing.generic import Type_LUT_Iterator

cit = Type_LUT_Iterator('cit')

@cit.register(tuple)
@cit.register(DC.All)
@cit.register(DC.Any)
@cit.register(DC.Sequence)
def cit_all(iterator, item):
	for sub_item in item:
		yield from iterator(sub_item)

@cit.register(DC.Type_Instance)
@cit.register(DC.Identity)
@cit.register(DC.Call_And_Compare_Return_Value)
@cit.register(type(DC.Always_True))
@cit.register(type(DC.Never_True))
def cit_ti(iterator, item):
	yield from ()

@cit.register(DC.Capture)
@cit.register(DC.Capture_Remaining)
def cit_ti(iterator, item):
	yield item.name

@cit.register(DC.Structure_Match)
def cit_sm(iterator, item):
	for key, sub_condition in item.value.items():
		yield from iterator(sub_condition)

