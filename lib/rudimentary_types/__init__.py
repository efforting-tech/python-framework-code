class ordered_set:
	def __init__(self, initial):
		self._dict = dict.fromkeys(initial)

	def __iter__(self):
		yield from self._dict

	def __len__(self):
		return len(self._dict)
