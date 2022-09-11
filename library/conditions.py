class instance_of:
	def __init__(self, type):
		self.type = type

	def __call__(self, item):
		return isinstance(item, self.type)

	def __repr__(self):
		return f'instance_of({self.type!r})'
