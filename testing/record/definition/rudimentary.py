from efforting.mvp6.record.rudimentary import create_record, define_simple_record, iter_type_members, iter_instance_members_and_values
from efforting.mvp6 import symbol

test = create_record('test',
	('stuff', 'thing',),
	dict(
		setting='repr(self)',
		info='None',
	),
	evaluation_scope = locals(),
	local_updates={'self': symbol.target.instance},
)

t2 = create_record('t2', ('more_things',), bases=(test,))


print(t2(123, 456, 2).setting)


q = t2('hello', 'yo', 5, info='hello')


define_simple_record('yo', 'things', 'stuff')
print(yo.things)


print(q.setting)

print(*iter_type_members(type(q)))
print(*iter_instance_members_and_values(q))


define_simple_record('factory', 'function', positional=symbol.argument.all.positional, wee=symbol.argument.all.named, wee2=symbol.argument.all.named)

print(factory(int, 1, 2, 3, stuff=123, things=456).wee2)
