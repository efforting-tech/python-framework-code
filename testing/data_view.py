from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Sequence, Structure
from efforting.mvp6 import symbol

class View_Definition_Resolver_Depth_Limiter(Structure):
	resolver = M.positional()
	limit = M.positional()
	restore_value = M.positional()

	def __enter__(self):
		self.restore_value = self.resolver.limit_value
		self.resolver.limit_value = self.limit
		print('ENTER')

	def __exit__(self, et, ev, tb):
		self.resolver.limit_value = self.restore_value
		print('EXIT')

class View_Definition_Resolver(Structure):
	definition = M.positional()
	visited = M.positional(factory=set)
	limit_value = M.positional(None)

	def limit(self, depth):
		return View_Definition_Resolver_Depth_Limiter(self, depth)

	def resolve(self, name):
		MISS = object()	#TODO local symbol
		if (value := self.definition._values.get(name, MISS)) is not MISS:
			return value

		if self.limit_value is not None:
			self.limit_value -= 1
			if self.limit_value <= 0:
				print('LIMIT REACHED')
				return symbol.unresolved

		conversion_rule = self.definition._view_definition.members[name]
		print(conversion_rule)
		if conversion_rule in self.visited:
			print('CYCLE DETECTED')
			return symbol.unresolved

		self.visited.add(conversion_rule)

		if (value := conversion_rule.resolve(self)) is not symbol.unresolved:
			self.definition._values[name] = value
		return value


class View_Definition_Instance(Structure):
	_view_definition = M.positional()
	_values = M.positional(factory=dict)

	def __getattr__(self, name):
		if (value := View_Definition_Resolver(self).resolve(name)) is not symbol.unresolved:
			return value
		else:
			raise AttributeError(f'could not resolve {name!r}')


class View_Definition(Structure):
	name = M.positional(None)
	members = M.all_named()

	def __call__(self, **values):
		return View_Definition_Instance(self, values)




class Node(Structure):
	def __or__(self, other):
		return Branch(self, other)

	def __and__(self, other):
		return All(self, other)

class Branch(Node):
	branches = M.all_positional()

	def resolve(self, resolver):
		with resolver.limit(1):
			for b in self.branches:
				if (sub_value := b.resolve(resolver)) is not symbol.unresolved:
					return sub_value

			return symbol.unresolved


#Not sure if we would need this so it is not implemented for now
class All(Node):
	sub_conditions = M.all_positional()

class Field_Conversion_Rule(Node):
	field_name = M.positional()
	converter = M.positional()


	def resolve(self, resolver):
		if (value := resolver.resolve(self.field_name)) is not symbol.unresolved:
			return self.converter(value)

		return symbol.unresolved


view_def = View_Definition(
	int = Field_Conversion_Rule('float', int) | Field_Conversion_Rule('string', int),
	float = Field_Conversion_Rule('string', float) | Field_Conversion_Rule('int', float),
	string = Field_Conversion_Rule('int', str) | Field_Conversion_Rule('float', str),
)

instance = view_def(int=42)

print(repr(instance.float))

print('---')
print(repr(instance.float))
