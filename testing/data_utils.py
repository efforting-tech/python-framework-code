from efforting.mvp6.data_utils import Dict_As_Object_Read_Interface

stuff = dict(
	hello = 'world',
	thing = dict(
		stuff = 123,
	),
)

o = Dict_As_Object_Read_Interface(stuff)

print(o.thing.stuff)