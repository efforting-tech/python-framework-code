from .. import record as R
from ... import Symbol as S
from ..symbol import Local_Symbol as LS

# To-Do List: (by chatgpt)

#     Simplify Condition System:
#         Reduce the number of distinct condition classes by composing them from simpler conditions (e.g., Unequality as a negation of Equality).
#         Implement basic conditions like Greater_Than, Less_Than, and their combinations (e.g., Greater_Than_or_Equal_To).
#         Consider integrating negations for common conditions where applicable.

#     Define Higher-Level Coverage:
#         Move complex condition combinations (e.g., range conditions like Inclusive_Range, Exclusive_Range) to a higher-level module for better modularity and coverage.
#         Ensure the higher-level module handles full condition coverage.

#     Plan Match-Like System for Optimization:
#         Design a pattern-matching system to automatically convert between conditions and optimize expressions.
#         Predefine optimized expressions for common patterns, especially those that can use sets or hashes for efficiency.
#         Consider how to integrate optimizations based on rule patterns for common usage.

#	 Handle Naming Dualities in Higher-Level Module:
#	     Account for multiple names representing the same logic (e.g., negating inclusive_inside results in exclusive_outside).
#	     Ensure the higher-level module maps and handles these equivalences cleanly.




class Abstract_Condition(R.Record):
	pass

class Abstract_Property_Condition(Abstract_Condition):
	pass


class Abstract_Composed_Condition(Abstract_Condition):
	sub_conditions: R.Field(kind=S.Member.Kind.All_Positional)

class Abstract_Value_Condition(Abstract_Condition):
	value: R.Field()

class Abstract_Range_Condition(Abstract_Condition):
	low: R.Field()
	high: R.Field()



class Abstract_Instance_of(Abstract_Condition):
	type: R.Field()

class Instance_of(Abstract_Instance_of):
	def check(self, item):
		return isinstance(item, self.type)

class Class_of(Abstract_Instance_of):
	def check(self, item):
		return isinstance(item, type) and isinstance(self.type, item)


class Abstract_Subclass_of(Abstract_Condition):
	type: R.Field()

class Subclass_of(Abstract_Subclass_of):
	def check(self, item):
		return isinstance(item, type) and issubclass(item, self.type)

class Strict_Subclass_of(Abstract_Subclass_of):
	def check(self, item):
		return isinstance(item, type) and item is not self.type and issubclass(item, self.type)

class Direct_Subclass_of(Abstract_Subclass_of):
	def check(self, item):
		return self.type in item.__bases__

class Abstract_Superclass_of(Abstract_Condition):
	type: R.Field()

class Superclass_of(Abstract_Superclass_of):
	def check(self, item):
		return isinstance(item, type) and issubclass(self.type, item)

class Strict_Superclass_of(Abstract_Superclass_of):
	def check(self, item):
		return isinstance(item, type) and item is not self.type and issubclass(self.type, item)

class Direct_Superclass_of(Abstract_Superclass_of):
	def check(self, item):
		return item in self.type.__bases__

class Equality(Abstract_Value_Condition):
	def check(self, item):
		return item == self.value

class Unequality(Abstract_Value_Condition):
	def check(self, item):
		return item != self.value

class Greater_Than(Abstract_Value_Condition):
	def check(self, item):
		return item > self.value

class Greater_Than_or_Equal_To(Abstract_Value_Condition):
	def check(self, item):
		return item >= self.value

class Less_Than(Abstract_Value_Condition):
	def check(self, item):
		return item < self.value

class Less_Than_or_Equal_To(Abstract_Value_Condition):
	def check(self, item):
		return item <= self.value


class Inclusive_Range(Abstract_Range_Condition):
	def check(self, item):
		return self.low <= item <= self.high

class Low_Inclusive_Range(Abstract_Range_Condition):
	def check(self, item):
		return self.low <= item < self.high

class High_Inclusive_Range(Abstract_Range_Condition):
	def check(self, item):
		return self.low < item <= self.high

class Exclusive_Range(Abstract_Range_Condition):
	def check(self, item):
		return self.low < item < self.high



class Any_Subcondition(Abstract_Composed_Condition):

	def check(self, item):
		assert self.sub_conditions	#Undefined behavior

		for c in self.sub_conditions:
			if c.check(item):
				return True
		return False

class All_Subconditions(Abstract_Composed_Condition):
	def check(self, item):
		assert self.sub_conditions	#Undefined behavior

		for c in self.sub_conditions:
			if not c.check(item):
				return False
		return True

#This one could actually be used to implement both Any_Subcondition and All_Subconditions among many other useful structures (like, exactly one match, at least one match and so on)
class Subset_of_Subconditions(Abstract_Composed_Condition):
	min_true_count: R.Field(kind=S.Member.Kind.Named) = None
	max_true_count: R.Field(kind=S.Member.Kind.Named) = None
	min_false_count: R.Field(kind=S.Member.Kind.Named) = None
	max_false_count: R.Field(kind=S.Member.Kind.Named) = None

	def check(self, item):
		assert self.sub_conditions	#Undefined behavior

		true_list = list()
		false_list = list()

		for c in self.sub_conditions:
			if c.check(item):
				true_list.append(c)
				if self.max_true_count is not None and len(true_list) > self.max_true_count:
					return False
			else:
				false_list.append(c)
				if self.max_false_count is not None and len(flase_list) > self.max_false_count:
					return False


		if self.min_true_count is not None and len(true_list) < self.min_true_count:
			return False

		if self.min_false_count is not None and len(true_list) < self.min_false_count:
			return False

		return True


class Negated(Abstract_Condition):
	sub_condition: R.Field(kind=S.Member.Kind.All_Positional)

	def check(self, item):
		return not self.sub_condition.check(item)


class Attribute_Condition(Abstract_Property_Condition):
	attribute: R.Field()
	sub_condition: R.Field()

	def check(self, item):
		MISS = LS('MISS')

		if (to_check := getattr(item, self.attribute, MISS)) is not MISS:
			return self.sub_condition.check(to_check)

		return False


class Item_Condition(Abstract_Property_Condition):
	key: R.Field()
	sub_condition: R.Field()

	def check(self, item):
		MISS = LS('MISS')

		if (to_check := item.get(self.key, MISS)) is not MISS:
			return self.sub_condition.check(to_check)

		return False



class Return_Condition(Abstract_Property_Condition):
	sub_condition: R.Field()
	positional: R.Field(factory=tuple)
	named: R.Field(factory=dict)

	def check(self, item):

		if callable(item):
			try:
				to_check = item(*self.positional, **self.named)
				return self.sub_condition.check(to_check)
			except:
				pass

		return False

def Optional(sub_condition):
	return Subset_of_Subconditions(sub_condition)