from efforting.mvp6.state_machine import State_Manager, Transition
from efforting.mvp6 import symbol


S = symbol.aggregator.status

sm = State_Manager(S, dict(
	abort = Transition(S.Aborted, {S.Pending, S.Working}),
	finish = Transition(S.Finished, {S.Pending, S.Working}),
	work = Transition(S.Working, {S.Pending, S.Working}),
	reset = Transition(S.Pending),
))


smi = sm(assert_validity=False)

print(dir(smi.interface))	#abort, finish, reset, work

print(smi.interface.abort(), smi)	#True State(Aborted)
print(smi.interface.finish(), smi)	#False State(Aborted)
print(smi.interface.reset(), smi)	#True State(Pending)
print(smi.interface.work(), smi)	#True State(Working)
print(smi.interface.work(), smi)	#True State(Working)

