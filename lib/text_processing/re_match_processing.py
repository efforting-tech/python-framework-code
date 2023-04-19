from .. import type_system as RTS
from ..type_system.bases import public_base

class match_iterator(public_base):
	match = RTS.positional()

	_positional_group_iterator = RTS.state()
	_pending_positional = RTS.state(None)

	@RTS.initializer
	def init(self):
		self._positional_group_iterator = iter(self.match.groups())

	@property
	def positional(self):
		return self.match.groups()

	@property
	def named(self):
		return self.match.groupdict()

	@property
	def text(self):
		return self.match.group(0)


	#No idea why I did it like this
	# @property
	# def pending_positional(self):
	# 	if self._pending_positional is None:
	# 		self._pending_positional = next(self._positional_group_iterator)

	# 	return self._pending_positional


	@property
	def pending_positional(self):
		return next(self._positional_group_iterator)
