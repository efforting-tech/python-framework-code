from .. import symbol
from .. import ABC

@ABC.Factory
class Evaluate_In_Scope:
	def __init__(self, expression, scope, local_updates):
		self.expression = expression
		self.scope = scope
		self.local_updates = local_updates

	def __call__(self, descriptor, target):
		if self.local_updates:
			scope = dict(self.scope)
			for key, value in self.local_updates.items():
				if value is symbol.target.instance:
					scope[key] = target
				else:
					scope[key] = value
		else:
			scope = self.scope

		setattr(target, descriptor.name, eval(self.expression, scope))