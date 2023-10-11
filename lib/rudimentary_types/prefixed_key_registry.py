class base_key_registry:
	pass

class integer_key_allocator:
	#TODO - we should rename these things a bit, this one is only the allocator
	def __init__(self, start=0):
		self.pending = start

	def allocate(self):
		id = self.pending
		self.pending += 1
		return id

class integer_key_registry(base_key_registry):
	def __init__(self, start=0):
		self.pending = start
		self.by_identity = dict()
		self.by_id = dict()

	def register(self, identity):
		id = self.pending
		self.by_identity[identity] = id
		self.by_id[id] = identity
		self.pending += 1
		return id

	def maybe_register(self, identity):
		if (existing := self.by_identity.get(identity)) is not None:
			return existing
		else:
			id = self.pending
			self.by_identity[identity] = id
			self.by_id[id] = identity
			self.pending += 1
			return id

	def register_using_factory(self, factory):
		id = self.pending
		identity = factory(id)
		self.by_identity[identity] = id
		self.by_id[id] = identity
		self.pending += 1
		return id

	def allocate(self):
		id = self.pending
		self.pending += 1
		return id

	def register_allocated(self, id, identity):
		self.by_identity[identity] = id
		self.by_id[id] = identity

	def __iter__(self):
		yield from self.by_identity

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