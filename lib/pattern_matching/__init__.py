#TODO - deprecate this in favor of priority_translator

#from . import condition

from .. import type_system as RTS
from .. import abstract_base_classes as ABC
from .. import api
from ..symbols import register_symbol

from ..iteration_utils.branchable_iterator import branchable_iterator
from ..type_system.bases import standard_base as base

from collections import abc as cABC

MISS = register_symbol('internal.miss')

#  ___
# | _ ) __ _ ___ ___ ___
# | _ \/ _` (_-</ -_|_-<
# |___/\__,_/__/\___/__/


#TBD - currently we use instance_of for matched_pattern but maybe we should use the symbol in the ABC tree instead? (we should also check if we use the wrong instance_of in other places)
#	However - currently ABC registry is incomplete and we can't rely on it (so should probably solve that fairly soon)

@ABC.register_class_tree('internal.pattern.match')
class matched_pattern(base, abstract=True):
	pattern = RTS.positional()

@ABC.register_class_tree('internal.pattern')
class pattern(base, abstract=True):

	def match(self, item):
		return self.match_bi(branchable_iterator((item,)))
		# bi = branchable_iterator((item,))
		# if (m := self.match_bi(bi)) and bi.is_empty():	#Must check that we matched the whole thing
		# 	return m

	match_bi = api.function(api.instance_of(matched_pattern) | api.identity(None), api.instance_of(branchable_iterator))

@ABC.register_class_tree('internal.pattern.condition', 'internal.condition')
class condition(pattern, abstract=True):
	pass

class sequential_condition(condition, abstract=True):
	pass

#  ___     _       _ _   _            ___             _ _ _   _
# | _ \_ _(_)_ __ (_) |_(_)_ _____   / __|___ _ _  __| (_) |_(_)___ _ _  ___
# |  _/ '_| | '  \| |  _| \ V / -_) | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
# |_| |_| |_|_|_|_|_|\__|_|\_/\___|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/

class primitive_condition(condition, abstract=True):
	def match_bi(self, iterator):
		if (value := iterator.pop(MISS)) is MISS:
			return

		if self.check_primitive_condition(value):
			return matched_value(self, value)


	def match(self, item):
		return self.check_primitive_condition(item)


class custom_primitive_condition(primitive_condition):
	function = RTS.positional()

	def check_primitive_condition(self, item):
		return self.function(item)

class identity(primitive_condition):
	identity = RTS.positional()

	def check_primitive_condition(self, item):
		return item is self.identity

class instance_of(primitive_condition):
	type = RTS.positional()

	def check_primitive_condition(self, item):
		return isinstance(item, self.type)

class subclass_of(primitive_condition):
	type = RTS.positional()

	def check_primitive_condition(self, item):
		return isinstance(item, type) and issubclass(item, self.type)

class type_identity(primitive_condition):
	identity = RTS.positional()

	def check_primitive_condition(self, item):
		return item.__class__ is self.identity

class value_equals(primitive_condition):
	value = RTS.positional()

	def check_primitive_condition(self, item):
		return item == self.value

class contains_value(primitive_condition):
	value = RTS.positional()

	def check_primitive_condition(self, item):
		return isinstance(item, cABC.Container) and isinstance(self.value, cABC.Hashable) and self.value in item

class value_in(primitive_condition):
	collection = RTS.positional()

	def check_primitive_condition(self, item):
		return isinstance(item, cABC.Hashable) and isinstance(self.value, cABC.Container) and item in self.value




class primitive_transformation(condition, abstract=True):
	def match_bi(self, iterator):
		if (value := iterator.pop(MISS)) is MISS:
			return

		return matched_value(self, self.transform(value))

class conditional_collect(primitive_transformation):
	sub_condition = RTS.positional()

	def transform(self, item):
		if isinstance(item, cABC.Iterable):
			return tuple(i for i in item if self.sub_condition.match(i))

class custom_translator(primitive_transformation):
	function = RTS.positional()

	def transform(self, item):
		return self.function(item)




class sub_value_condition(condition):
	translator = RTS.positional()
	condition = RTS.positional()

	def match_bi(self, iterator):
		if (value := iterator.pop(MISS)) is MISS:
			return

		if sub_value := self.translator.match(value):
			return self.condition.match(sub_value.get_value())







#  _   _                     _ _ _   _               _   __  __      _      _
# | | | |_ _  __ ___ _ _  __| (_) |_(_)___ _ _  __ _| | |  \/  |__ _| |_ __| |_  ___ _ _ ___
# | |_| | ' \/ _/ _ \ ' \/ _` | |  _| / _ \ ' \/ _` | | | |\/| / _` |  _/ _| ' \/ -_) '_(_-<
#  \___/|_||_\__\___/_||_\__,_|_|\__|_\___/_||_\__,_|_| |_|  |_\__,_|\__\__|_||_\___|_| /__/


#IMPORTANT - I don't like these - they should probably not be here at all!

# class unconditional(condition, abstract=True):
# 	def match_bi(self, iterator):
# 		if (value := iterator.pop(MISS)) is MISS:
# 			return

# 		return matched_value(self, self.process_value(value))



# class capture_type(unconditional):
# 	def process_value(self, value):
# 		return value.__class__

# class collect_object_values(unconditional):
# 	def process_value(self, value):
# 		return value.__dict__.values()



#  ___                        _   _      _    ___             _ _ _   _
# / __| ___ __ _ _  _ ___ _ _| |_(_)__ _| |  / __|___ _ _  __| (_) |_(_)___ _ _  ___
# \__ \/ -_) _` | || / -_) ' \  _| / _` | | | (__/ _ \ ' \/ _` | |  _| / _ \ ' \(_-<
# |___/\___\__, |\_,_\___|_||_\__|_\__,_|_|  \___\___/_||_\__,_|_|\__|_\___/_||_/__/
#             |_|

class sequence(sequential_condition):
	sequence = RTS.all_positional()

	def match_sequence(self, sub_iterator):
		result = list()
		for sub_pattern in self.sequence:
			if m := sub_pattern.match_bi(sub_iterator):
				result.append(m)
			else:
				return
		return result


	def match_bi(self, iterator):
		#note - we will be checking that we got the entire sequence here but we probably want to be able to have a "starts-with" feature later on - not sure how that will look though
		if (pending := iterator.pop(MISS)) is not MISS:
			sub_iterator = branchable_iterator(pending)
			if (match := self.match_sequence(sub_iterator)) is not None:
				if sub_iterator.is_empty():
					return matched_sequence(self, match)


#   ___           _
#  / __|__ _ _ __| |_ _  _ _ _ ___
# | (__/ _` | '_ \  _| || | '_/ -_)
#  \___\__,_| .__/\__|\_,_|_| \___|
#           |_|

class capture(sequential_condition):
	positional = RTS.all_positional()
	named = RTS.all_named()

	@property
	def sequence(self):
		return (*self.positional, *self.named.values())

	def match_bi(self, iterator):
		if (match := sequence.match_sequence(self, iterator)) is not None:
			return matched_capture(self, match)


#  __  __      _      _
# |  \/  |__ _| |_ __| |_  ___ ___
# | |\/| / _` |  _/ _| ' \/ -_|_-<
# |_|  |_\__,_|\__\__|_||_\___/__/

class matched_sequence(matched_pattern):
	sequence = RTS.positional()

class matched_capture(matched_sequence):
	pass

	def get_positional(self):
		return self.sequence[:len(self.pattern.positional)]

	def get_named(self):
		return dict(zip(self.pattern.named, self.sequence[len(self.pattern.positional):]))

	def get_value(self):
		#TBD - maybe this should return bound arguments from inspect or something?
		return self.get_positional(), self.get_named()


class matched_value(matched_pattern):
	value = RTS.positional()

	def get_value(self):
		return self.value

#  _   _ _   _ _ _ _   _
# | | | | |_(_) (_) |_(_)___ ___
# | |_| |  _| | | |  _| / -_|_-<
#  \___/ \__|_|_|_|\__|_\___/__/

#TODO - make a generic dumper that we can extend from each module - or make a dumping protocol?
#		A dumping protocol have the drawback of not being able to dump stuff from third party types
#		so adding entries to a dumper is probably better
def dump_match(item, indent='', title=''):
	if isinstance(item, matched_value):
		print(f'{indent}{title}{item.__class__.__qualname__:<20}{item.value!r}')
	elif isinstance(item, matched_capture):
		pos, named = item.get_positional(), item.get_named()
		print(f'{indent}{title}{item.__class__.__qualname__:<20}({len(pos)} positionals, {len(named)} named)')

		for index, sub_item in enumerate(pos, 1):
			dump_match(sub_item, f'{indent}   ', f'#{index:<12}')

		for key, sub_item in named.items():
			dump_match(sub_item, f'{indent}   ', f'{key!r:<13}')

	elif isinstance(item, matched_sequence):
		print(f'{indent}{title}{item.__class__.__qualname__:<20}({len(item.sequence)} elements)')
		for index, sub_item in enumerate(item.sequence, 1):
			dump_match(sub_item, f'{indent}   ', f'#{index:<8}')
	else:
		raise Exception(item)


