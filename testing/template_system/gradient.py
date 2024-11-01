#Case study creaing a color gradient

from efforting.mvp6.core import record as _R

class Abstract_Math(_R.Record):
	def __sub__(self, other):
		return subtract(self, other)

	def __mul__(self, other):
		return multiply(self, other)

class operation(Abstract_Math):
	pass

class binary_operation(operation):
	A: _R.Field() = None
	B: _R.Field() = None

class subtract(binary_operation):
	def compute(self):
		return self

class multiply(binary_operation):
	def compute(self):
		return self

class color(Abstract_Math):
	R: _R.Field() = 0.0
	G: _R.Field() = 0.0
	B: _R.Field() = 0.0

class lerp(operation):
	A: _R.Field() = 0.0
	B: _R.Field() = 1.0
	f: _R.Field() = 0.5

	def compute(self):
		return (self.B - self.A) * self.f




from efforting.mvp6.core.dispatcher import Type_LUT_Transformer, Instance_LUT_Reducer

D = Type_LUT_Transformer()

D_mul = Type_LUT_Reducer()

@D_mul.register_function(binary_operation, binary_operation)
def proc(A, B):
	print(A, B)

@D_mul.register_function(binary_operation, float)
def proc(A, B):
	print(A, B)


@D.register_function(multiply)
def proc(item):
	return D_mul.dispatch_item((item.A, item.B))



print(D.dispatch_item(lerp(lerp(f=0.2), lerp(f=0.8), 0.3).compute().compute()))