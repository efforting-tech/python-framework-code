def instantiate(cls):
	return cls()

class return_value:
	def __init__(self, value):
		self.value = value


@instantiate
class ignore_call:
	def __call__(self, *pos, **named):
		pass