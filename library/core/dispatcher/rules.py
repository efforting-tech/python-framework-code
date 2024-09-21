from .. import record as R
from ... import ABC

#TODO - maybe the action field should be renamed, maybe value is better, but then instead of rule maybe we should call it conditional value?
#TODO - think about whether we should think about API around things utilizing aggregators

#TODO - figure out how we want to chain dispatchers

# class Fallback_Rule(R.Record):
# 	fallback: R.Field(type=ABC.Sequence, factory=list)

# 	def action(self, dispatcher, item, result):
# 		print('ACT!', item)

# 		for d in self.fallback:
# 			#print('SUBRES', d.dispatch_node(item))

# 			print(d.regulations.aggregate_matches(item))

# 		exit()


class Core_Rule(R.Record):
	pass

class Regex_Rule(Core_Rule):	#TODO - override signature so we can have action in core_rule but still have regex_rule(cond, act)
	pattern: R.Field(type=ABC.Regex.Compiled)
	action: R.Field() = True

	def match(self, item):
		return self.pattern.fullmatch(item)

class Unconditional_Rule(Core_Rule):
	action: R.Field() = True

	def match(self, item):
		return True

class LUT_Rule(Unconditional_Rule):
	pass
