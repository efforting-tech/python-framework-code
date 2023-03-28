


def ensure_mutable_sequence(item):
	#TODO - use more rule sets and ABC - we may also employ some generic API for some mutable_sequence ABC
	if isinstance(item, (tuple, list)):
		return [ensure_mutable_sequence(ss) for ss in item]
	elif isinstance(item, number):
		return item
	else:
		raise Exception('Not supported yet', item)




def maybe_get_tuple_of_integers(item):
	#TODO - add more checks and also allow for rule based extension
	if isinstance(item, tuple):
		if all(isinstance(i, integer) for i in item):
			return item
