
class pre_rts_function:
	def __init__(self, target):
		self.target = target

	def __get__(self, instance, owner):
		return self.target(instance, owner)


class bound_pre_rts_function:
	def __init__(self, instance, owner):
		self.instance = instance
		self.owner = owner

def get_pre_rts_fields(type):
	pending = dict()
	for base in reversed(type.mro()):
		if default_values := getattr(base, '_default_values', None):
			for key, value in base._default_values.items():
				match value:
					case rts_factory():
						pending[key] = value()
					case _:
						pending[key] = value

	return pending

class bound_pre_rts_initializer(bound_pre_rts_function):
	def __call__(self, *positional, **named):
		pending = get_pre_rts_fields(self.owner)

		#TODO - before we introduced positional we had a lot of pre_rts initializations that were by name, we should convert the ones that makes sense

		p_iter = iter(positional)
		for name, value in zip(pending, p_iter):
			assert name not in named
			named[name] = value

		assert not tuple(p_iter)	#TODO - use better function that tries to do next() instead

		superfluous = set(named) - set(pending)
		assert not superfluous, f'Unknown settings: {superfluous}'

		pending.update(named)
		self.instance.__dict__.update(pending)



class bound_pre_rts_representer(bound_pre_rts_function):
	def __call__(self):
		gen = ((f, dv, getattr(self.instance, f, dv)) for f, dv in get_pre_rts_fields(self.owner).items())
		inner = ', '.join(f'{f}={v!r}' for f, dv, v in gen if dv != v)
		return f'{self.owner.__qualname__}({inner})'

class pre_rts_type:
	_default_values = dict()
	__init__ = pre_rts_function(bound_pre_rts_initializer)
	__repr__ = pre_rts_function(bound_pre_rts_representer)

class rts_factory:
	def __init__(self, factory, *positional, **named):
		self.factory = factory
		self.positional = positional
		self.named = named

	def __call__(self):
		return self.factory(*self.positional, **self.named)

