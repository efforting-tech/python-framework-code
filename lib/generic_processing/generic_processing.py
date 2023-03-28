from .. import rudimentary_type_system as RTS
from ..rudimentary_type_system.bases import public_base

#TODO - we are providing something similar in "conditional data processing", we should harmonize
#	maybe all data processing things should be under one thing and then the specializations, create nicer structure

class generic_processor(public_base):
	#TODO - we may later add features for per item filtering, per item target_type and such but for now we are starting simple
	rules = RTS.all_positional()


	def process_sequence_iteratively(self, sequence):	#TODO create some nice API for all the process X features throughout the project
		for item in sequence:
			yield self.process_item(item)

	def process_item(self, item):
		for condition, action in self.rules:
			if match := condition.match(item):
				return action.take_action(self, match, item)	#TODO maybe we should support other things than just returning - similar to how other places do this - we should collect them all in one place

		raise Exception(item)


class dispatch_action(public_base):
	pass

class yield_filtered_value(dispatch_action):
	filter = RTS.positional()

	def take_action(self, processor, match, item):
		return self.filter(item)
