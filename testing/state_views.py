from efforting.mvp6.state_view import State_Interface_Definition, State_Mapping
from efforting.mvp6 import symbol, symbol_factory as SF


#DEMO - create some symbols
L = SF.Symbol('local')
SF.register_symbols_at_target(L, '''

	math.number
	math.set
	unit.mass
	unit.time


''')

#Create two interface definitions
math_if = State_Interface_Definition('math_if', N=L.math.number, S=L.math.set)
unit_if = State_Interface_Definition('unit_if', M=L.unit.mass, T=L.unit.time)

#Create a common state with one entry
state = State_Mapping({L.math.number: 123})

#Create two interfaces
math = math_if(state)
unit = unit_if(state)

math.S = 'the set'	#Write the other math entry
unit.M, unit.T = 'kg', 'seconds'
print(math)	#State_Interface(N=123, S='the set')
print(unit)	#State_Interface(M='kg', T='seconds')

print(state) #State_Mapping(S'math.number': 123, S'math.set': 'the set', S'unit.mass': 'kg', S'unit.time': 'seconds')

#Access math interface from unit interface (by calling the interface definition)
print(math_if(unit))	#State_Interface(N=123, S='the set')
#Access math interface from unit interface (by calling the interface)
print(math(unit))		#State_Interface(N=123, S='the set')
