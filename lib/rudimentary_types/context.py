
#Actually - maybe not use this at all


# #TODO - this is an early sketch - figure out how to traverse descendents to build builtins
# #	probably figure out a configuration-feature to go along with the RTS so we can do merges and updates on descendants
# class context:
# 	def __init__(self):
# 		self.locals = dict()
# 		self.globals = dict(self.builtins.__dict__)

# 	def eval_expression(self, expression):
# 		return eval(expression, self.globals, self.locals)

# 	#For now we define this but a subclass would currently overwrite it rather than extend it
# 	class builtins:
# 		pass
