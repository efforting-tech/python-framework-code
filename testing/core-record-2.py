from dataclasses import dataclass
from efforting.mvp6 import Strict_Symbol as S


#TODO - move to other module
def popattr(target, name, default=S.Action.Raise_Exception):
	if hasattr(target, name):
		value = getattr(target, name)
		delattr(target, name)
		return value
	elif default is S.Action.Raise_Exception:
		raise AttributeError(f'Required attribute {name!r} was not set for {target!r}')	#TODO - custom exception
	else:
		return default


class Core_Type_System:
	pass


@dataclass
class Register_Required_Interfaces:
	target: Core_Type_System
	interfaces: tuple

	def __call__(self, target_type):
		self.target.register_required_interfaces(target_type, self.interfaces)
		return target_type



import dataclasses


@dataclass
class Field_Definition:
	field_definition: field_definition = None
	type: type = None
	name: str = None
	description: str = None

	def copy(self, **updates):
		state = dict(self.__getstate__())
		state.update(updates)
		return type(self)(**state)

	def updated_copy(self, update):
		state = dict(self.__getstate__())

		for name, value in update.__getstate__().items():
			if value == S.Not_Set:
				continue
			else:
				state[name] = value

		return type(self)(**state)


#TODO - utility function for creating update/delta of structures ( SSoT )
Field_Definition_Update = dataclass(type('Field_Definition_Update', (), dict(
	__annotations__ =  {f: None for f in Field_Definition.__dataclass_fields__},
	**{f: S.Not_Set for f in Field_Definition.__dataclass_fields__}
)))



@dataclass
class Data_Descriptor:
	system: Core_Type_System
	field_definition: Field_Definition

	def __get__(self, instance, owner):
		if instance is None:
			return self


	def __set__(self, instance, value):
		pass





@dataclass
class Type_System(Core_Type_System):
	field_lut: dict = dataclasses.field(default_factory=dict)


	@property
	def Record(self):

		class Record:
			def __init_subclass__(cls):
				fields = self.collate_existing_fields(cls)

				for name, field_definition in self.pop_pending_fields(cls).items():
					match field_definition:
						case Field_Definition():
							self.init_subclass_process_field_definition(cls, field_definition.copy(name=name))

						case Field_Definition_Update():
							self.init_subclass_process_field_definition(cls, fields[name].updated_copy(field_definition))

						case str():
							raise NotImplementedError('TODO - str')
						case type():
							self.init_subclass_process_field_definition(cls, Field_Definition(
								type = field_definition,
								name = name,
							))

						case unhandled:
							raise Exception(unhandled)

		return Record



	def Interface(self, name):
		pass

	def Require_Interfaces(self, *interfaces):
		return Register_Required_Interfaces(self, interfaces)

	def Field(self, type=None, name=None, description=None):
		return Field_Definition(
			type = type,
			name = name,
			description = description,
		)

	def Update_Field(self, type=S.Not_Set, name=S.Not_Set, description=S.Not_Set):
		return Field_Definition_Update(
			type = type,
			name = name,
			description = description,
		)

	def init_subclass_process_field_definition(self, target, field_definition):
		if (fields := self.field_lut.get(target)) is None:
			self.field_lut[target] = {field_definition.name: field_definition}
		else:
			fields[field_definition.name] = field_definition

		#TODO - create data descriptors
		self.create_data_descriptors(target, field_definition)

	def create_data_descriptors(self, target, field_definition):
		print(target, field_definition, id(field_definition))
		dd = Data_Descriptor(self, field_definition)
		dd.__doc__ = field_definition.description or f'Member {field_definition.name!r} of {target!r}'
		setattr(target, field_definition.name, dd)

	def register_required_interfaces(self, target_type, interfaces):
		pass

	def collate_existing_fields(self, cls):
		#Collate existing fields
		result = dict()
		for base in cls.mro():
			if fields := self.field_lut.get(base):
				result.update(fields)

		return result

	def pop_pending_fields(self, cls):
		result = dict()
		if anno := popattr(cls, '__annotations__'):
			for name, field_definition in anno.items():
				result[name] = field_definition

		return result

TS = Type_System()


IFA = TS.Interface('IFA')
IFB = TS.Interface('IFB')

@TS.Require_Interfaces(IFA)
class test(TS.Record):
	member: str


@TS.Require_Interfaces(IFB)
class subtest(test):
	member: TS.Update_Field(description='This field is pretty great')

#print(test.member)
#print(subtest.member)
#m = subtest()

#print(subtest.member.__doc__)

print(subtest().member)
