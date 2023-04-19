





#NOTE - We may add things here later but we have to be careful because when we try to import things deeper in the library, those things might depend on this
#		this may be a temporary issue because we are currently rewriting some things - but either way, this is the package ingress, it should probably be populated lastly, if at all

# from . import abstract_base_classes as abc	#FIGURE OUT - Do we want this in this namespace or why is it imported here?
# from .abstract_base_classes import interfaces
# from .resource_management import get_path	#TO DOCUMENT - document the use cases for anything that is included in this namespace since it is the root of the library

# #TO DECIDE - is this used by anything? Should it be different? What feature is this associated with?
# #NOTE - it seems this is utilized by the experiment local-web-service as part of an improved typing system for use with the web service
# def auto_convert(value, target):
# 	if isinstance(value, target):
# 		return value
# 	elif isinstance(target, interfaces.auto_conversion):
# 		return target.convert(value)
# 	else:
# 		#TO-DOCUMENT	Document this error
# 		raise TypeError(f'Can not convert {value!r} into {target}')

