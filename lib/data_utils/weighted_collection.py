from .. import type_system as RTS
from ..type_system.bases import public_base

#TODO - move to proper location in library
class top_most_weighted_collection(public_base):
	length = RTS.positional()
	queue = RTS.factory(list)
	#min = RTS.state(None)
	#max = RTS.state(None)

	def store(self, item, weight):
		#todo - optimize this - this is just for testing (this would be where min/max comes into play)
		self.queue.append((item, weight))
		self.queue = list(sorted(self.queue, reverse=True, key=lambda x: x[1])[:self.length])

#TODO - move to proper location in library
class top_most_weighted_mapping(public_base):
	length = RTS.positional()
	mapping = RTS.factory(dict)
	#min = RTS.state(None)
	#max = RTS.state(None)

	def store(self, key, item, weight):
		#todo - optimize this - this is just for testing (this would be where min/max comes into play)
		self.mapping[key] = (item, weight)
		self.mapping = dict(sorted(self.mapping.items(), reverse=True, key=lambda x: x[1][1])[:self.length])

#TODO - move to proper location in library
class top_most_weighted_set(public_base):
	length = RTS.positional()
	set = RTS.factory(dict)	#Because we need ordered set
	#min = RTS.state(None)
	#max = RTS.state(None)

	def store(self, item, weight):
		#todo - optimize this - this is just for testing (this would be where min/max comes into play)
		self.set[(item, weight)] = None
		self.set = dict.fromkeys(sorted(self.set, reverse=True, key=lambda x: x[1])[:self.length])
