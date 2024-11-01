from efforting.mvp6.core import record as R
from efforting.mvp6.core.dispatcher import Type_LUT_Processor
from efforting.mvp6 import Symbol as S

class Some_Dispatcher(R.Record):
	D: R.Field(kind=S.Member.Kind.Hierarchial) = Type_LUT_Processor()

	@D.register_function(float)
	def f(self, item):
		return 'Float'


class Derived_Dispatcher(Some_Dispatcher):
	D = Type_LUT_Processor()

	@D.register_function(int)
	def f(self, item):
		return 'Integer'

# Here Derived_Dispatcher will have two rules while Some_Dispatcher will have but one.
print(Derived_Dispatcher.D.regulations)
print(Some_Dispatcher.D.regulations)


#OUTPUT

# Type_LUT_Regulations(rules={<class 'float'>: <function Some_Dispatcher.f at 0x7c9ceca6af20>, <class 'int'>: <function Derived_Dispatcher.f at 0x7c9ceca7c040>} fallback_rule=None LUT_key=<class 'type'>)
# Type_LUT_Regulations(rules={<class 'float'>: <function Some_Dispatcher.f at 0x7c9ceca6af20>} fallback_rule=None LUT_key=<class 'type'>)


