from dataclasses import dataclass
from typing import Optional
from .. import Symbol as S, Symbol as DFS, ABC


from ..introspection import stack_limit

REPR_STACK_LIMIT = stack_limit(2)


#Record is used very early so we need to forward declare some symbols here

factory_context = None

class Core_Record:
	def __init_subclass__(cls):
		pending_fields = dict()

		#Collate current fields
		for base in reversed(cls.mro()):
			if base is object:
				continue

			for name, info in base.__annotations__.items():
				match info:
					case Field():
						pending_fields[name] = info
						#print(info.owner, base)
						assert not info.owner or info.owner is base	#TODO - not sure if this will happen during normal ops
						info.owner = base

						if info.kind is S.Member.Kind.Hierarchial:
							if cls is base:
								continue

							#print('HI!', base, getattr(base, name), '→', cls)

							setattr(cls, name, getattr(base, name).create_child(getattr(cls, name, None)))


					#TODO - maybe we should have Field_Replace as well which would take ownership. Then we could also have abstract fields which would be just like Field but be required to be implemented down the line
					case Field_Update():
						new_state = dict(pending_fields[name].__getstate__())	#BUGFIX - do not make shallow copy
						new_state.update(info)
						pending_fields[name] = Field(**new_state)


					case unhandled:
						raise Exception(unhandled)

		cls._record_fields = pending_fields
		cls.__match_args__ = tuple(pending_fields.keys())		#TODO - consider exluding fields from match_args

		# NOTE - Here we could take actions such as subclass initialization of record fields
		#for name, info in pending_fields.items():
			#print(name, info)


	def __init__(self, *positionals, **named):
		#TODO - care about type/ensure_type ?
		global factory_context
		positionals = list(positionals)

		cls = type(self)
		for name, info in cls._record_fields.items():

			pending_value = S.Not_Set

			if info.kind == S.Member.Kind.Positional_or_Named:
				if positionals:
					assert name not in named
					pending_value = positionals.pop(0)
				else:
					pending_value = named.pop(name, S.Not_Set)

			elif info.kind == S.Member.Kind.Positional:
				if positionals:
					assert name not in named
					pending_value = positionals.pop(0)

			elif info.kind == S.Member.Kind.Named:
				pending_value = named.pop(name, S.Not_Set)

			elif info.kind == S.Member.Kind.All_Positional:
				pending_value = tuple(positionals)
				positionals.clear()

			elif info.kind == S.Member.Kind.All_Named:
				pending_value = dict(named)
				named.clear()

			#NOTE - later we may want named subsets of things
			elif info.kind in (S.Member.Kind.Internal, S.Member.Kind.Hierarchial):
				pass

			else:
				raise Exception(info.kind)

			if pending_value == S.Not_Set and info.default is not S.Not_Set:	#TODO - we have some mixed == and is because we had a silly idea for the symbols. We should get back to is
				pending_value = info.default

			if pending_value == S.Not_Set:
				factory_context = dict(
					parent = factory_context,
					name = name,
					info = info,
					positionals = positionals,
					named = named,
					instance = self,
				)

				if info.factory:
					if isinstance(info.factory, ABC.Factory.Contextual):
						pending_value = info.factory(factory_context)
					else:
						pending_value = info.factory()

				factory_context = factory_context['parent']

			if pending_value != S.Not_Set:
				super().__setattr__(name, pending_value)



		assert not positionals, f'Unexpected positional arguments: {positionals}'
		assert not named, f'Unexpected keyword arguments: {named}'





	def __repr__(self):

		with REPR_STACK_LIMIT:
			try:
				pieces = list()
				MISS = object()
				for f, i in type(self)._record_fields.items():

					if i.repr is False:
						pass
					elif callable(i.repr):
						pieces.append(i.repr(self, f, i))
					elif (value := getattr(self, f, MISS)) is MISS:
						pieces.append(f'{f}=N/A')
					else:
						pieces.append(f'{f}={value!r}')

				inner = ' '.join(filter(bool, pieces))

			except RecursionError:
				inner = '\N{HORIZONTAL ELLIPSIS}'

		return f'{type(self).__qualname__}({inner})'


class Record(Core_Record):
	def __setattr__(self, name, value):
		if name.startswith('_'):
			super().__setattr__(name, value)
		else:
			cls = type(self)
			info = cls._record_fields[name]
			assert info.mutable, f'Field {cls}.{name} ({info.owner}) is not mutable.'
			super().__setattr__(name, value)

#TODO - figure out why we wanted this and decide whether it is worthy of existing
class Dynamic_Record(Core_Record):
	def __setattr__(self, name, value):
		if name.startswith('_'):
			super().__setattr__(name, value)
		else:
			cls = type(self)
			if info := cls._record_fields.get(name):
				assert info.mutable, f'Field {cls}.{name} ({info.owner}) is not mutable.'

			super().__setattr__(name, value)


@ABC.Factory.Contextual
@dataclass
class Bound_Factory:
	target:			callable

	def __call__(self, context):
		return self.target(context['instance'])



@dataclass
class Core_Field_Record:
	type: 			Optional[type] = None
	ensure_type: 	Optional[bool] = False
	mutable:		Optional[bool] = True
	owner:			Optional[type] = None
	factory:		Optional[callable] = None
	repr:			Optional[callable] = True
	default:		Optional[object] = S.Not_Set
	kind:			object = S.Member.Kind.Positional_or_Named	#TODO fix up

class Field(Core_Field_Record):
	pass

class Field_Update(dict):
	pass

