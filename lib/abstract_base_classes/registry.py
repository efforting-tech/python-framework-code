from . import register_abstract_base_classes, register_specific_class, register_conversion, register_condition


class collection:
	(generic, identifiers) = register_abstract_base_classes(*'collection.generic collection.identifiers'.split())

register_specific_class('collection.generic')(list)
register_specific_class('collection.generic')(tuple)
register_specific_class('collection.generic')(set)
register_specific_class('collection.generic')(frozenset)


#Maybe use some generic flattener function?
def iter_flattened_identifiers(sequence):
	for sub_item in sequence:
		yield from collection.identifiers._auto_convert(sub_item)

class tuple_of_identifiers(tuple):	#This is used so that we know that we don't need further conversion - maybe we should find a nicer way for this?
	pass

register_condition('collection.identifiers', lambda s: isinstance(s, tuple_of_identifiers))
register_conversion('collection.identifiers', str, lambda s: tuple(dict.fromkeys(s.split())))	#dict used as ordered set here
register_conversion('collection.identifiers', collection.generic, lambda s: tuple(dict.fromkeys(iter_flattened_identifiers(s))))	#dict used as ordered set here