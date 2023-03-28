#Install default formatter
from .formatting import space_wrapping_object_accessor
from .types import base, OP, pending_operation, function, operation, primitive_token
from . import operations
from .matrix_base import matrix
from .vector_base import vector


def representation(self):
	return eval(f'f{self.format!r}', {}, space_wrapping_object_accessor(self))

#Maybe we should put these in an interface instead
base.__repr__ = representation
primitive_token.__repr__ = representation



def resolve_pending(e):
	def lookup(op):
		if candidate := getattr(operations, op._target.name, None):
			if isinstance(candidate, type) and issubclass(candidate, operation):	#TODO maybe use ABC or the condition system?
				return candidate

	match e:
		case pending_operation(operation=op, operands=operands) if (rtype := lookup(op)):
			return rtype(*map(resolve_pending, operands))

		case function(operands=operands):
			return e.__class__(*map(resolve_pending, operands))

	return e

