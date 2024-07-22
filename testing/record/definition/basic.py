class test_abc(Test):
	from efforting.mvp6.record.base.public import Structure
	import efforting.mvp6.record.member as M
	from efforting.mvp6.record.member import utils as MU

	from efforting.mvp6 import ABC


	class Test(Structure):
		stuff = M.positional(factory=list)
		#thing = M.positional(factory=MU.factory(list, (1, 2, 3)))

	assert isinstance(Test.stuff.descriptor.init, ABC.Factory)

	assert Test().stuff == []