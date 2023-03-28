class base_key_registry:
	pass

class prefixed_key_registry(base_key_registry):
	def __init__(self, prefix, start=0):
		self.prefix = prefix
		self.pending = start
		self.by_identity = dict()
		self.by_id = dict()

	def register(self, identity):
		id = f'{self.prefix}{self.pending}'
		self.by_identity[identity] = id
		self.by_id[id] = identity
		self.pending += 1
		return id

	def register_using_factory(self, factory):
		id = f'{self.prefix}{self.pending}'
		identity = factory(id)
		self.by_identity[identity] = id
		self.by_id[id] = identity
		self.pending += 1
		return id

	def allocate(self):
		id = f'{self.prefix}{self.pending}'
		self.pending += 1
		return id

	def register_allocated(self, id, identity):
		self.by_identity[identity] = id
		self.by_id[id] = identity

	def __iter__(self):
		yield from self.by_identity