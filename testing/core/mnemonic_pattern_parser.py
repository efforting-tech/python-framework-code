from mnemonic_pattern_tokenizer import main_tokenizer, Word, Text, Whitespace
from efforting.mvp6.core.data_conditions import record as DCR
from efforting.mvp6.iteration import branchable_iterator

from efforting.mvp6.core.dispatcher import Type_LUT_Reducer, Type_LUT_Translator
from efforting.mvp6.core import record as R


pattern = 'Define {name as category} Project[:]'


condition = DCR.Equality((
	Word('define'),
	Whitespace(),
	Word('project'),
	DCR.Optional(Text(':')),
))


class Match(R.Record):
	condition: R.Field()
	value: R.Field()


#NEXT UP - TODO - Stateful matcher might make it easier to deal with lazy/greedy expansion


#NOTE - Sequence comparator need to be able to expand Lazy_Expansion and possibly Greedy_Expansion
seq_comparator = Type_LUT_Translator()


@seq_comparator.register_function(Text)
@seq_comparator.register_function(Word)
def match(iterator, condition):
	entry = iterator.pop()
	match entry:
		case Word(value=value) | Text(value=value) if condition.value == value.lower():
			return Match(condition, entry)


@seq_comparator.register_function(DCR.Subset_of_Subconditions)
def match(iterator, condition):
	i = iterator.branch()
	true_m = 0
	false_m = 0
	entries = list()
	for sc in condition.sub_conditions:
		if sm := seq_comparator.bound_dispatch_item(i, sc):
			entries.append(sm)
			true_m += 1
			if true_m == condition.max_true_count:	#This of course can't happen if it is None
				break
		else:
			entries.append(None)
			false_m += 1
			if fase_m == condition.max_false_count:	#This of course can't happen if it is None
				break

	if ((condition.min_true_count is None or condition.min_true_count <= true_m) and
		(condition.min_true_count is None or condition.min_true_count <= true_m)):
		iterator.synchronize_with(i)
		return Match(condition, entries)



@seq_comparator.register_function(Whitespace)
def match(iterator, condition):
	match iterator.pop():
		case Whitespace():
			return True

		case unhandled:
			return False



@seq_comparator.register_function(DCR.Equality)
def match(iterator, condition):
	match condition.value:
		case tuple() | list():

			i = iterator.branch()
			entries = list()
			for sc in condition.value:
				if sm := seq_comparator.bound_dispatch_item(i, sc):
					entries.append(sm)
				else:
					return

			iterator.synchronize_with(i)
			return Match(condition, entries)

		case unhandled:
			raise Exception(unhandled)


result = main_tokenizer.tokenize('define project:').tokens
r = seq_comparator.bound_dispatch_item(branchable_iterator(iter(result)), condition)



#r = comparator.reduce(condition, result)

print(r)




# print(Word('define') == Word('define'))
# print(Word('define') == Word('Define'))

# print(main_tokenizer.tokenize(pattern).tokens)
