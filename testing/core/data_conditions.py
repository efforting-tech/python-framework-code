from efforting.mvp6.core import record as R
from efforting.mvp6 import Symbol as S

from efforting.mvp6.core.data_conditions import record as DCR




print(DCR.All_Subconditions(DCR.Equality(123), DCR.Instance_of(int)).check(123))
print(DCR.All_Subconditions(DCR.Equality(123), DCR.Instance_of(int)).check(123.0))
print(DCR.Greater_Than(120).check(123))
print(DCR.Inclusive_Range(10, 20).check(21))


print('---')
print(DCR.Subset_of_Subconditions(DCR.Equality(123), DCR.Instance_of(int), min_true_count=1, max_true_count=1).check(123))
print(DCR.Subset_of_Subconditions(DCR.Equality(123), DCR.Instance_of(int), min_true_count=1, max_true_count=1).check(500))
print(DCR.Subset_of_Subconditions(DCR.Equality(123), DCR.Instance_of(int), min_true_count=1, max_true_count=1).check(123.0))

print('---')

print(DCR.Return_Condition(DCR.Equality('HELLO'), positional=('hello',)).check(str.upper))




# #Shorthands
# def Type_Identity(*type_id_list):
# 	if len(type_id_list) == 1:
# 		[type_id] = type_id_list
# 		return Type_Condition(Object_Identity(type_id))
# 	else:
# 		return Any_Subcondition(*(Type_Condition(Object_Identity(type_id)) for type_id in type_id_list))

# def Equality(*value_list):
# 	if len(value_list) == 1:
# 		[value_id] = value_list
# 		return Object_Equality(value_id)
# 	else:
# 		return Any_Subcondition(*(Object_Equality(value) for value in value_list))

# def Identity(*id_list):
# 	if len(id_list) == 1:
# 		[identity] = id_list
# 		return Object_Identity(identity)
# 	else:
# 		return Any_Subcondition(*(Object_Identity(identity) for identity in id_list))

# def Instance_of(*type_list):
# 	if len(type_list) == 1:
# 		[instance_type] = type_list
# 		return Instance_Condition(instance_type)
# 	else:
# 		return Any_Subcondition(*(Instance_Condition(it) for it in type_list))

# def Subclass_of(*type_list):
# 	if len(type_list) == 1:
# 		[instance_type] = type_list
# 		return Subclass_Condition(instance_type)
# 	else:
# 		return Any_Subcondition(*(Subclass_Condition(it) for it in type_list))



# c = Type_Identity(str)
# print(c)
# print('   ', c.check('hello'), c.check(123))
# c = Instance_of(str, int, float)
# print(c)
# print('   ', c.check('hello'), c.check(123), c.check(1+2j))
# c = Equality(10, 20)
# print(c)
# print('   ', c.check('hello'), c.check(10.0))

# c = Subclass_of(int)
# print(c)
# print('   ', c.check(bool))


# # Type contained in
# # Item contained in
# # Identity contained in
# # Instance is one of
# # Subclass is one of

# # Type is
# # Identity is
# # Value equals
# # Instance of
# # Subclass of


