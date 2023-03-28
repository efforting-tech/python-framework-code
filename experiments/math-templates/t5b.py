from t5_testing_types import *
import sys

class condition(public_base):
	pass


class tensor:
	pass


class rank_is(condition):
	value = RTS.positional()

class T:
	def add_requirements(*requirements):
		f = sys._getframe(1).f_locals
		f['__requirements'] = f.get('__requirements', ()) + requirements


#condition tree similar to abc tree
class scalar(tensor):
	T.add_requirements(
		C.tensor.rank_is(0),
	)

class vector(tensor):
	T.add_requirements(
		C.tensor.rank_is(1),
	)

class matrix(tensor):
	T.add_requirements(
		C.tensor.rank_is(2),
	)


print(matrix.__requirements)