from dataclasses import dataclass
from typing import Optional

class Record:
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


					case Field_Update():
						new_state = pending_fields[name].__getstate__()
						new_state.update(info)
						pending_fields[name] = Field(**new_state)

					case unhandled:
						raise Exception(unhandled)

		cls._record_fields = pending_fields

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
					continue

			if target_type := info.type:
				if et := info.ensure_type:
					if not isinstance(value, target_type):
						print('TARGET', target_type, value)
						print(et.convert(value, target_type))
						exit()
						#value = target_type(value)

				assert isinstance(value, target_type), f'Unable to set {type(self)}.{name} ({info.owner}). Expected type {target_type} but got {type(value)}.'

			setattr(self, name, value)



@dataclass
class Core_Field_Record:
	type: 			Optional[type] = None
	ensure_type: 	Optional[bool] = False
	mutable:		Optional[bool] = None
	owner:			Optional[type] = None

class Field(Core_Field_Record):
	pass

class Field_Update(dict):
	pass

