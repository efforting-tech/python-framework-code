from efforting.mvp6.aggregation import Aggregator, First_Result, Result_List, Result_Set, Sorted_List, Last_Result, Random_Result, Counter
from efforting.mvp6.record import member as M


#Demo

class Error_Example(Aggregator):
	value = M.positional(factory=list)

	def aggregate(self, entry):
		if entry == 'how':
			self.abort('No questions allowed!')
		else:
			self.register_work()
			self.value.append(entry)


for t in (First_Result, Last_Result, Random_Result, Result_List, Result_Set, Error_Example, Sorted_List, Counter):
	a = t()

	for v in ['hello', 'world', 'how', 'are', 'you', '?', '?', '?']:
		if not a.accepting_work:
			break

		a.aggregate(v)

	print(f'Result for {t.__qualname__}: {a.value} ({a.state._name}, {a.error!r})')

# Output

# Result for First_Result: hello (Finished, None)
# Result for Result_List: ['hello', 'world', 'how', 'are', 'you', '?', '?', '?'] (Working, None)
# Result for Result_Set: {'are', 'how', 'hello', 'you', 'world', '?'} (Working, None)
# Result for Error_Example: ['hello', 'world'] (Aborted, 'No questions allowed!')
# Result for Sorted_List: ['?', '?', '?', 'are', 'hello', 'how', 'world', 'you'] (Working, None)

