from ..symbols import create_symbol
#TODO - this should be its own module

#TO PONDER - I don't remember what the notes under here was referring to so it will remain for a bit
#	This is used when we want to check something with transparent references and we should mark what places uses this or not
#	These markings should be something like: "Not applicable", "Purposefully not conforming" or "Conforming"
#	This way we can have an idea of coverage
#	Best would be to keep this in a separate database so that in the case of changes we can use a checksum verification and know things may be out of date

import types

MISS = create_symbol('internal.miss')

TYPE_PROXY_DIRECTORY = dict()

#This one will use silent fallback
def proxy_resolve(item, item_type=None):
	if item_type is None:
		item_type = type(item)

	if proxy_field := TYPE_PROXY_DIRECTORY.get(item_type):
		if (proxy_value := getattr(item, proxy_field, MISS)) is not MISS:
			return proxy_resolve(proxy_value)

	return item



class proxy_registrator_used_with_subclass_init:
	def __init__(self, proxy_field):
		self.proxy_field = proxy_field

	#Note - this one is different because it is used in __init_subclass__
	#TODO - make a wrapper that filters the arguments and use that with the regular abc_registrator and get rid of the base generic_abc_registrator
	def __call__(self, target, **type_options):
		#TBD - should we raise exception if we are changing an existing value?
		TYPE_PROXY_DIRECTORY[target] = self.proxy_field


class pending_class_tree_proxy_registration:
	def __init__(self, proxy_field):
		self.proxy_field = proxy_field

	def __call__(self, target):
		scr = proxy_registrator_used_with_subclass_init(self.proxy_field)

		target_func = getattr(target.__init_subclass__, '__func__', None)

		if isinstance(target.__init_subclass__, types.BuiltinFunctionType):
			target.__init_subclass__ = classmethod(scr)
		elif target_func is scr:
			pass #Already hooked into this particular one
		# elif isinstance(target_func, generic_abc_registrator):	#Do we need this?
		# 	target.__init_subclass__ = classmethod(abc_registrator_used_with_subclass_init(*self.path_list, *target_func.path_list))
		elif target_func:
			target.__init_subclass__ = classmethod(call_sequence(scr, target_func))
		else:
			raise Exception(target)

		scr(target)

		return target


def register_class_tree_proxy_resolution(proxy_field):
	return pending_class_tree_proxy_registration(proxy_field)
