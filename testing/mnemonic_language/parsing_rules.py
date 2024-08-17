


from efforting.mvp6.matching import data_condition as DC

from efforting.mvp6.mnemonic_language import parsing_rules as PR

#print()

#PR.mnemonic_comparator().compare_items(DC.Equality(123), 123)

#PR.mnemonic_comparator().compare_items(DC.Sequence(DC.Equality(123),), [123])
#PR.mnemonic_comparator().compare_items(DC.Sequence(DC.Equality(123),), 123)


expected = DC.Sequence(
	DC.Equality(123),
	#DC.Capture_Remaining('stuff', DC.Type_Identity(int)),
	DC.Capture_Remaining('stuff'),
	DC.Equality(456),
	DC.Equality(789),
)

mc = PR.mnemonic_comparator()
mc.compare_items(expected, [123, 1, 2, 3, 456, 789])
print(mc.captures)