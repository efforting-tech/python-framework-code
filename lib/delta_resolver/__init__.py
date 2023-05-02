#NOTE - when it comes to resolvers that may either give replacement or delete+insert, we should try to prioritize replacement, at least for non primitives
#		this is so that when we are creating a delta for a composit type, we can compare replaced branches as well.
#		This will likely be implemented using a high weight for replacement operations, but this system is not yet implemented