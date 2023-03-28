#TODO - move this - rename it too - it should be in the not yet created test directory

def get_state(target):
	return (
		tuple(target.rows),
		tuple(tuple(k.lut.items()) for k in target.keys.values())
	)


class state_test:
	def __init__(self, *targets):
		self.targets = targets

	def __enter__(self):
		self.initial_states = tuple(get_state(t) for t in self.targets)

	def __exit__(self, et, ev, tb):
		current_states = tuple(get_state(t) for t in self.targets)
		assert self.initial_states == current_states
