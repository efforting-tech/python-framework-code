from ..symbols import register_symbol
from .introspection import get_fields
from .rts_types import initializer, replace_initializer
MISS = register_symbol('internal.miss')
from collections import defaultdict


def run_initializers(target_class, instance):
	#Run additional initializers
	pending_initializers = defaultdict(list)

	for base in reversed(target_class.mro()):
		for name, item in base.__dict__.items():
			if isinstance(item, initializer):	#TODO abc, abstract
				pending_initializers[name].append(item)
			elif isinstance(item, replace_initializer):
				pending_initializers[name] = [item]

	for initializers in pending_initializers.values():
		for init in initializers:
			init.__get__(instance, target_class)()


def standard_fields(*positional, **named):
	#Note that target is part of positional to prevent name clash with users fields
	pending_positionals = list(positional)
	target = pending_positionals.pop(0)
	for f in get_fields(target.__class__).values():
		f.init(target, pending_positionals, named)

	assert not (pending_positionals or named), f'{target.__class__} got unexpected arguments: {pending_positionals}, {named}'	#TODO format nicer

	#Run additional initializers
	run_initializers(target.__class__, target)


@classmethod
def from_config(target_class, config, *positional, **named):
	return from_state.__func__(target_class, config._resolve(), *positional, **named)


@classmethod
def from_state(target_class, state, *positional, **named):
	unutilized = set(state.keys())
	instance = object.__new__(target_class)
	pending_positionals = list(positional)

	for key, field in get_fields(target_class).items():
		if (named_value := named.pop(key, MISS)) is not MISS:
			unutilized.discard(key)
			setattr(instance, key, named_value)
		elif (state_value := state.get(key, MISS)) is not MISS:
			unutilized.discard(key)
			setattr(instance, key, state_value)
		else:
			field.init(instance, pending_positionals, named)

	run_initializers(target_class, instance)
	return instance

def abstract(*positional, **named):
	#Note that target is part of positional to prevent name clash with users fields
	target = positional[0]
	fqn = f'{target.__class__.__module__}.{target.__class__.__qualname__}'
	raise Exception(f'Class {fqn!r} is abstract and must not be instantiated.')