
class item_filter:
	def __init__(self, condition=None):
		self.condition = condition

	def __call__(self, source):
		if IC := self.condition:
			yield from (i for i in source if IC(i))
		else:
			return source





class dict_item_filter:
	def __init__(self, key=None, value=None, key_condition=None, value_condition=None):
		self.key = key
		self.value = value
		self.key_condition = key_condition
		self.value_condition = value_condition

	def __call__(self, source):
		K, V, KC, VC = self.key, self.value, self.key_condition, self.value_condition

		if KC and VC:
			if K and V:
				return ((K(k), V(v)) for k, v in source if KC(k) and VC(v))
			elif K:
				return ((K(k), v) for k, v in source if KC(k) and VC(v))
			elif V:
				return ((k, V(v)) for k, v in source if KC(k) and VC(v))
			else:
				return ((k, v) for k, v in source if KC(k) and VC(v))
		elif KC:
			if K and V:
				return ((K(k), V(v)) for k, v in source if KC(k))
			elif K:
				return ((K(k), v) for k, v in source if KC(k))
			elif V:
				return ((k, V(v)) for k, v in source if KC(k))
			else:
				return ((k, v) for k, v in source if KC(k))
		elif VC:
			if K and V:
				return ((K(k), V(v)) for k, v in source if VC(v))
			elif K:
				return ((K(k), v) for k, v in source if VC(v))
			elif V:
				return ((k, V(v)) for k, v in source if VC(v))
			else:
				return ((k, v) for k, v in source if VC(v))
		else:
			if K and V:
				return ((K(k), V(v)) for k, v in source)
			elif K:
				return ((K(k), v) for k, v in source)
			elif V:
				return ((k, V(v)) for k, v in source)
			else:
				return source