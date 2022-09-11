from threading import Lock

class counter:
	def __init__(self):
		self._state = dict()
		self._lock = Lock()

	def __getitem__(self, key):
		return self._state.get(key, 0)

	def increment(self, key, amount=1):
		with self._lock:
			new_value = self._state.get(key, 0) + amount

			if new_value:
				self._state[key] = new_value
			else:
				self._state.pop(key, None)

			return new_value

	def decrement(self, key, amount=1):
		with self._lock:
			new_value = self._state.get(key, 0) - amount

			if new_value:
				self._state[key] = new_value
			else:
				self._state.pop(key, None)

			return  new_value

