from .. import record as R
from ... import ABC



#TODO - we should have matches somewhere, maybe its own module?

#TODO - conditions should probably be separate and then we just use a simple rule in all the places
#		this will make it easier to reuse conditions in different rules

#TODO - we should probably remove regex_rule and unconditional_rule here and just use the data conditions

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

class Generic_Rule(Core_Rule):	#TODO - override signature so we can have action in core_rule but still have regex_rule(cond, act)
	condition: R.Field()
	action: R.Field() = True

	def match(self, item):
		return self.condition.check(item)


class Unconditional_Rule(Core_Rule):
	action: R.Field() = True

	def match(self, item):
		return True

class LUT_Rule(Unconditional_Rule):
	pass


class Tree_View_Regex_Rule(Core_Rule):	#TODO - override signature so we can have action in core_rule but still have regex_rule(cond, act)
	pattern: R.Field(type=ABC.Regex.Compiled)
	action: R.Field() = True

	def match(self, item):
		return self.pattern.fullmatch(item.title)


class Core_Match(R.Record):
	rule: R.Field()

class Node_Classification_Match(Core_Match):
	classification: R.Field()

def represent_classification_set(self, field, info):
	inner = ', '.join(sorted(i.__name__ for i in getattr(self, field)))
	return f'{field}={{{inner}}}'

class Node_Classification_Rule(Core_Rule):
	classification_set: R.Field(repr=represent_classification_set)
	action: R.Field() = True

	def match(self, item):
		if (classification := item.classification) in self.classification_set:
			return Node_Classification_Match(self, classification)
