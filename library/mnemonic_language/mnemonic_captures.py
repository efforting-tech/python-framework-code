from ..matching import data_condition as DC
from ..processing.generic import Type_LUT_Iterator

#TODO - better names for functions
#TODO - make sure we cover all things in DC (we should make helpers for this)



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
@cit.register(DC.Wrap_Capture)
@cit.register(DC.Pop_And_Push_Capture)
def cit_ti(iterator, item):
	yield from ()

@cit.register(DC.Capture)
@cit.register(DC.Capture_Remaining)
def cit_ti(iterator, item):
	yield item.name

@cit.register(DC.Call_Function)
def cit_ti(iterator, item):
	yield item.target_capture

@cit.register(DC.Update_Flag)
def cit_ti(iterator, item):
	yield item.capture


@cit.register(DC.Structure_Match)
def cit_sm(iterator, item):
	for key, sub_condition in item.value.items():
		yield from iterator(sub_condition)








cfit = Type_LUT_Iterator('cfit')

@cfit.register(tuple)
@cfit.register(DC.All)
@cfit.register(DC.Any)
@cfit.register(DC.Sequence)
def cfit_all(iterator, item):
	for sub_item in item:
		yield from iterator(sub_item)

@cfit.register(DC.Type_Instance)
@cfit.register(DC.Identity)
@cfit.register(DC.Call_And_Compare_Return_Value)
@cfit.register(type(DC.Always_True))
@cfit.register(type(DC.Never_True))
@cfit.register(DC.Wrap_Capture)
def cfit_ti(iterator, item):
	yield from ()

@cfit.register(DC.Capture)
@cfit.register(DC.Capture_Remaining)
def cfit_ti(iterator, item):
	yield item, 'name'

@cfit.register(DC.Call_Function)
def cfit_ti(iterator, item):
	yield item, 'target_capture'

@cfit.register(DC.Update_Flag)
def cfit_ti(iterator, item):
	yield item, 'capture'

@cfit.register(DC.Structure_Match)
def cfit_sm(iterator, item):
	for key, sub_condition in item.value.items():
		yield from iterator(sub_condition)


