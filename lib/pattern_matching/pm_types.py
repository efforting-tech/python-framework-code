raise Exception('dep')

from . import type_system as RTS
from . import abstract_base_classes as ABC


# #Maybe we need to have a base pattern matching api we can use to see when an item is even relevant
# #We could for instance have a requirement condition

# class pattern_api:
# 	requirement = api.field(api.identity(None))


# #Matchers specifically for objects with a member classification

# class classification:
# 	classification = field(required=True)


# 	__init__ = field_based_initializer
# 	__repr__ = field_based_representation('{self.classification}')





#These are simple boolean conditions for use in api definitions - we register them in two places
@ABC.register_class_tree('internal.pattern_matching')
class pattern_matching:
	__init__ = RTS.initialization.standard_fields
	__repr__ = RTS.representation.local_fields

class identity(pattern_matching):
	identity = RTS.positional()

class instance_of(pattern_matching):
	type = RTS.positional()

class subclass_of(pattern_matching):
	type = RTS.positional()

class type_identity(pattern_matching):
	type = RTS.positional()
