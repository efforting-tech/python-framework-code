from . import registry as _R

#TODO - synchronize with registry (maybe auto generate?) Actually might be better to use a symbol traversal thing for this but with different __call__
#CLARIFICATION - using a symbol traversal thing refers to how derivates of symbol_attribute_access_interface can be used as a dotted path callable.


#NOTE
#	This here was meant to be some sort of namespace but we should probably find a better way to define this namespace.
#	Otherwise all branches closest to the root act like separate roots and it just looks a bit inconsistent.
#	Also note that this is connected with feature DC
class collection:
	identifiers = _R.collection.identifiers._auto_convert