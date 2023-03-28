#Actually putting things in a sub library


from efforting.mvp4.math.functions import sin, cos
from efforting.mvp4.math.constants import e, i, pi
from efforting.mvp4.math import operations as op
from efforting.mvp4.math.types import real, operation, scalar, complex, imaginary, UNDEFINED
from efforting.mvp4.math import resolve_pending, matrix, vector
from efforting.mvp4.development_utils.introspection import introspect

#eulers_identity = e ** (i * pi) + 1 == 0
#print(eulers_identity)
#print(resolve_pending(eulers_identity))



vec2 = vector.empty(*'xy', name='vec2')
vec3 = vector.empty(*'xyz', name='vec3')
vec4 = vector.empty(*'xyzw', name='vec4')



M1 = matrix.empty(4, 4, dimensional_names = dict(row='xyzw', col='XYZW'))

class c:
	def __getitem__(self, key):
		print(key)

print(c()[2:3, 4:5])
print(c()[(2, 3), (5, 6)])



#print(M1.row[0])

exit()

M1.apply_serial_data(range(1, 17))



print(M1.get_swizzle_names())
#print(tuple(M1.x))

print(M1.row)



print(M1.get_traversal_order())
print(tuple(M1.iter_serial_coordinates()))

exit()

M1.apply_serial_data((
	1, 0, 0, 0,
	0, 1, 0, 0,
	0, 0, 1, 0,
	0, 0, 0, 1,
))





#M1.ordering = 'col', 'row'
#M1.apply_serial_data((10, 20, 30, 40, 50, 60, 70, 80, 90))
