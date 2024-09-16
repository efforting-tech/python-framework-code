from efforting.mvp6.core.text import Immutable_Tree_View, Mutable_Tree_View
from efforting.mvp6.core.symbol import Symbol_Node


# from efforting.mvp6 import Symbol_Root_Node, ABC_Root_Node, ABC, Symbol

# for n in Symbol_Root_Node.walk():
# 	print(n)

# for n in ABC_Root_Node.walk():
# 	print(n)

# print(ABC.Text.Line in ABC.Text)
# print(Symbol.Animal.Cat in Symbol)
# print(Symbol.Animal.Cat in Symbol.Animal.Dog)
# print(Symbol.Animal.Cat in Symbol.Animal.Cat)



# exit()




lv = Mutable_Tree_View('''

	this
		is
		a
		tree

''')

lv2 = Mutable_Tree_View('''

	here
		we
		have
	some
		other
		tree
	you
		see

''')


#print(lv[lv.first_line_index_with_content:lv.last_line_index_with_content+1].to_str())
#print(lv.copy(adjust_indent=-1, indention=' ·-- ').to_str())



print('======')
print(lv2.normal_str())
print('======')


# lv[4].text = '		hello'
# print(lv[4])
# lv.insert(4, '		more_stuff')


# for item in lv.iter_nodes():
# 	print('Title', item.title)
# 	print('-- Body ---')
# 	print(item.to_str(indention='  '))
# 	print('-- EOR ---')
