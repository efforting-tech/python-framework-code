from efforting.tech.template1.core import records as R
from efforting.tech.template1.core import Symbol, ABC

@ABC.Factory
class Test(R.Record):
	name: R.Field()
	all_the_pos: R.Field(kind=Symbol.Member.Kind.All_Positional)
	rules: R.Field(factory=list)

print(isinstance( Test(123, 'hello', 'world'), ABC.Factory))