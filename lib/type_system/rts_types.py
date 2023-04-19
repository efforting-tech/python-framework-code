from ..symbols import register_symbol
from ..pre_rts import pre_rts_type


#from ..symbols import register_symbol
import types

#TODO - maybe deprecate using simple_dynamic_initializer here?

NOT_ASSIGNED = register_symbol('internal.not_assigned')
SELF = register_symbol('internal.self')
ALL = register_symbol('internal.all')

#TODO - these should be a en enumeration
DEFAULT = register_symbol('internal.default')
SETTING = register_symbol('internal.setting')
MISS = register_symbol('internal.miss')

class field(pre_rts_type):

	#This is done in this particular way in order to harmonize future serialization of types utilizing the field class
	#field is likely to have things added to it in the future or maybe have defaults changed, this way we can include
	#a description of the field type itself as a part of the serialization process
	#Requirement: must not contain 'self'
	_default_values = dict(
		annotation =						None,
		factory =							None,
		factory_positionals =				None,
		factory_named =						None,
		name =								None,
		owner =								None,
		default =							NOT_ASSIGNED,
		required =							False,
		remaining_positionals =				False,
		remaining_named =					False,
		positional =						True,
		named =								True,
		read_only =							False,
		storable =							True,
		description = 						None,
		field_type = 						DEFAULT,
	)


	def init(self, target, positionals, named):
		if self.remaining_positionals:
			target.__dict__[self.name] = tuple(positionals)
			positionals.clear()
		elif self.remaining_named:
			target.__dict__[self.name] = dict(named)
			named.clear()
		elif self.positional and positionals:
			assert self.name not in named, f'Positional field `{self.name}´ is also in named arguments {named}'
			target.__dict__[self.name] = positionals.pop(0)
		elif self.named and (named_value := named.pop(self.name, NOT_ASSIGNED)) is not NOT_ASSIGNED:
			target.__dict__[self.name] = named_value
		elif self.factory:
			target.__dict__[self.name] = self.call_factory(target, positionals, named)
		elif self.default is not NOT_ASSIGNED:
			target.__dict__[self.name] = self.default
		elif self.required:
			raise Exception(f'Required field {self.name!r} not specified for {object.__repr__(target)}')	#We use object.__repr__ because target may not be fully initialized and its __repr__ method may not take that into consideration

	def call_factory(self, target, init_positionals, init_named):

		def transform_value(v):
			if v is SELF:	#TODO add support for init_pos and such?
				return target
			else:
				return v


		positionals = (transform_value(p) for p in (self.factory_positionals or ()))
		named = {name: transform_value(value) for name, value in (self.factory_named or {}).items()}
		return self.factory(*positionals, **named)


	def __set_name__(self, target, name):
		#NOTE - previously we would error out if name and owner was already set
		#		but this makes it so that we can't have another member be a reference to this field
		#		question is though .. should it be an error or should we upgrade to a constant field?
		#		For now I think we will keep the error and just make sure not to do it this way, automatic upgrades can be confusing
		assert self.name is None
		assert self.owner is None

		self.name = name
		self.owner = target

	def __get__(self, instance, owner):
		if instance is None:
			return self

		#TODO catch missing values and throw attributeerror
		#TODO - what do we think of factories? Should they be allowed here? Would they also assign and therefore cause mutation as the side effect of reading? Sounds sketchy..

		if (value := instance.__dict__.get(self.name, MISS)) is not MISS:
			return value
		elif (self.default is not NOT_ASSIGNED):
			return self.default
		else:
			raise AttributeError(f'{object.__repr__(instance)} does not have the attribute {self.name!r} set.')

	#TODO - __del__

	def __set__(self, instance, value):
		#TODO - checks
		if self.read_only:
			raise AttributeError(f'{self} is read only')

		instance.__dict__[self.name] = value

	def __delete__(self, instance):
		if self.read_only:
			raise AttributeError(f'{self} is read only')

		del instance.__dict__[self.name]


	def __repr__(self):
		if self.owner and self.name:
			return f'<{self.__class__.__name__} `{self.owner.__name__}.{self.name}´>'
		elif self.owner:
			return f'<{self.__class__.__name__} of `{self.owner.__name__}´>'
		elif self.name:
			return f'<{self.__class__.__name__} `{self.name}´>'
		else:
			return f'<{self.__class__.__name__} {hex(id(self))}>'

	def get_or_create_default(self, target):
		#TODO - check coverage of this?
		if self.default is not NOT_ASSIGNED:
			return self.default
		elif self.factory:
			return self.call_factory(target, (), {})
		elif self.remaining_positionals:
			return ()
		elif self.remaining_named:
			return {}
		else:
			return NOT_ASSIGNED



class field_configuration:
	def __init__(self, **configuration):
		#TODO - we could reuse the function creation function but for this particular purpose
		self.configuration = configuration

	def __call__(self, **additional_configuration):
		return field(**self.configuration, **additional_configuration)	#TODO - overrides? merges?


class initializer:
	def __init__(self, target):
		self.target = target

	def __get__(self, instance, owner):
		if instance is None:
			return self
		else:
			return types.MethodType(self.target, instance)


class replace_initializer:	#base classes above this will not be called but initializes below will
	def __init__(self, target):
		self.target = target

	def __get__(self, instance, owner):
		if instance is None:
			return self
		else:
			return types.MethodType(self.target, instance)


