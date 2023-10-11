from .. import type_system as RTS
from ..type_system.bases import public_base
from .operations import sequence as OP

class sequence_delta_applier(public_base):
	state = RTS.positional()

	def apply(self, operations):
		for op in operations:
			self.apply_single(op)

		return self.state

	def apply_single(self, op):
		match op:
			case OP.reversible.insert():
				head = self.state[:op.position]
				tail = self.state[op.position:]
				self.state = head + op.sequence + tail

			case OP.reversible.delete():
				head = self.state[:op.position]
				tail = self.state[op.position+len(op.deleted):]
				self.state = head + tail

			case OP.reversible.replace():
				head = self.state[:op.position]
				tail = self.state[op.position+len(op.replaced):]
				self.state = head + op.sequence + tail

			case OP.non_reversible.insert():
				head = self.state[:op.position]
				tail = self.state[op.position:]
				self.state = head + op.sequence + tail

			case OP.non_reversible.delete():
				head = self.state[:op.position]
				tail = self.state[op.position+op.length:]
				self.state = head + tail

			case OP.non_reversible.replace():
				head = self.state[:op.position]
				tail = self.state[op.position+op.length:]
				self.state = head + op.sequence + tail


			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

		return self.state

