from dataclasses import dataclass
from typing import Optional

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


					#TODO - maybe we should have Field_Replace as well which would take ownership. Then we could also have abstract fields which would be just like Field but be required to be implemented down the line
					case Field_Update():
						new_state = pending_fields[name].__getstate__()
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

		positionals = list(positionals)

		cls = type(self)
		for name, info in cls._record_fields.items():
			if positionals:
				assert name not in named
				value = positionals.pop(0)

			else:
				MISS = object()
				if (value := named.pop(name, MISS)) is MISS:
					if info.factory:				#TODO - support contextual factories
						value = info.factory()
					else:
						continue

			if target_type := info.type:
				if et := info.ensure_type:
					if not isinstance(value, target_type):
						print('TARGET', target_type, value)
						print(et.convert(value, target_type))
						exit()
						#value = target_type(value)

				assert isinstance(value, target_type), f'Unable to set {type(self)}.{name} ({info.owner}). Expected type {target_type} but got {type(value)}.'


			super().__setattr__(name, value)

		assert not positionals, f'Unexpected positional arguments: {positionals}'
		assert not named, f'Unexpected keyword arguments: {named}'



	def __repr__(self):

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


		inner = ' '.join(pieces)
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

class Dynamic_Record(Core_Record):
	def __setattr__(self, name, value):
		if name.startswith('_'):
			super().__setattr__(name, value)
		else:
			cls = type(self)
			if info := cls._record_fields.get(name):
				assert info.mutable, f'Field {cls}.{name} ({info.owner}) is not mutable.'

			super().__setattr__(name, value)



@dataclass
class Core_Field_Record:
	type: 			Optional[type] = None
	ensure_type: 	Optional[bool] = False
	mutable:		Optional[bool] = True
	owner:			Optional[type] = None
	factory:		Optional[callable] = None
	repr:			Optional[callable] = True

class Field(Core_Field_Record):
	pass

class Field_Update(dict):
	pass

