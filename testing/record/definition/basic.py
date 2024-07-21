from efforting.mvp6.record.base.public import Structure
import efforting.mvp6.record.member as M
from efforting.mvp6.record.member import utils as MU



class Test(Structure):
	stuff = M.positional(factory=list)
	#thing = M.positional(factory=MU.factory(list, (1, 2, 3)))

print(Test.stuff.descriptor.init)

#print(Test().stuff)