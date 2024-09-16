#TODO - should have Symbol and ABC here


from .core.abc import ABC


# from .core.abc import register_core_abc, ABC_REGISTRY, ABC_Node_Reference
# @register_core_abc('path.to.thing')
# class stuff:
# 	pass

# @register_core_abc('path.to.thing')
# @register_core_abc('path.to.other')
# class item:
# 	pass


# class sub_item(item):
# 	pass



# #print(isinstance(sub_item(), register_core_abc('path')))
# #print(ABC_REGISTRY.check_if_abc(register_core_abc('path.to.thing'), sub_item))

# #print(ABC_REGISTRY.cache)


# n = ABC_Node_Reference(register_core_abc('path.of.stuff'))

# print(register_core_abc('path.of.stuff') == n)

# @n
# class blargh:
# 	pass


# n._create_new = True
# print(n.thing.stuff.majig)

# print(isinstance(blargh(), n))

#exit()

#Testing
#from .core.interface.text.tree import Text_Tree_Interface
from .core.type.text import Immutable_Text_Tree

tt = Immutable_Text_Tree.from_str('''

	Hello
		World

''')

for n in tt.iter_nodes():
	print(n)