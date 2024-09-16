from efforting.mvp6.core.text import Immutable_Tree_View
from efforting.mvp6.core.symbol import Symbol_Node


from efforting.mvp6 import Symbol_Root_Node, ABC_Root_Node, ABC, Symbol

for n in Symbol_Root_Node.walk():
	print(n)

for n in ABC_Root_Node.walk():
	print(n)

print(ABC.Text.Line in ABC.Text)
print(Symbol.Animal.Cat in Symbol)
print(Symbol.Animal.Cat in Symbol.Animal.Dog)
print(Symbol.Animal.Cat in Symbol.Animal.Cat)



exit()




lv = Immutable_Tree_View('''

	this
		is
		a
		tree

	that
		has
			a
			bunch
		of
			branches
			and
				stuff
			right
''')





for item in lv.iter_nodes():
	print('Title', item.title)
	print('-- Body ---')
	print(item.to_str(indention='  '))
	print('-- EOR ---')
