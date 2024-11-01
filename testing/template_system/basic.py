from efforting.mvp6.template_system.processor import Macro
from efforting.mvp6.template_system.introspection import Dumper
from efforting.mvp6.template_system.render import Renderer, Renderer2
from efforting.mvp6.core.dispatcher import Type_LUT_Processor
from efforting.mvp6.core.text import Immutable_Tree_View




P = Macro('''

	def stuf():
		§ include thing
		§ emit: some_node
		pass #We will not do anything special in «current function».

''').result



r = Renderer()
r.context['some_node'] = Immutable_Tree_View.from_str('''

	# Hello World!

''').normal()

r.render(P)

print('-.--')
for item in r.result.result:
	print(item)

#Dumper().dump(P)

print('----')

r2 = Renderer2()



r3 = r2.render_block(r.result.result)


print(r3)
