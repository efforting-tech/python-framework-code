
class Pending_Decorator:
	def __init__(self, finalizer):
		self.finalizer = finalizer

	def __call__(self, target):
		return self.finalizer(target)


