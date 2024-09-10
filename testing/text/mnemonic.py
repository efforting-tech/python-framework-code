from efforting.mvp6.mnemonic_language.bootstrap import bootstrap_dispatcher

from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M
from efforting.mvp6 import ABC

from efforting.mvp6.document import create_text_tree_document_from_str

@ABC.Decorator
class store_dict(Structure):
	target = M.positional()
	name = M.positional(None)

	def __call__(self, entry):
		name = self.name or entry.__name__
		self.target[name] = entry
		return entry

@store_dict(bootstrap_dispatcher.state.execution_context.locals, 'AST')
class AST:
	class type_identity(Structure):
		identity = M.positional()



@store_dict(bootstrap_dispatcher.state.execution_context.locals)
def get_first_arg(expression):
	import ast
	#[e] = ast.parse('lambda yo, /, pos=456, *hello, thing=123, **stuff: None').body
	[e] = ast.parse(f'lambda {expression}: None').body

	a = e.value.args

	args = tuple(a for a in (*a.posonlyargs, *a.args, a.vararg, *a.kwonlyargs, a.kwarg) if a)
	return args[0].arg


test_tree = create_text_tree_document_from_str('''

	mnemonic tree processor: test_processor
		setup:
			all captures

		mnemonic function: greet {pattern as whom}
			return f'Hello {whom}!'


	mnemonic tree processor: dispatch_definition_processor
		setup:
			all captures

		mnemonic structure: type identity[:] {pattern as identity}
			return AST.type_identity

	amend current processor:
		setup:
			all captures
			ps.node
			ctx.dispatch_definition_processor

		mnemonic function: type lut processor[:] {signature}

			print(signature)

			#pdef = dispatch_definition_processor.on_behalf_of(dispatcher).dispatch_tree(node.body).value
			#print(name, pdef, get_first_arg(args))

	type lut processor: tp2(value)

		type identity: int
			return f'Integer({value})'

		type identity: str
			return f'String({value})'



''', normalize_block=True)


#mlp.context.set('hello', 'world')
bootstrap_dispatcher.dispatch_tree(test_tree)

tt2 = create_text_tree_document_from_str('''

	greet World


''', normalize_block=True)



#print(bootstrap_dispatcher.state.context['test_processor'].dispatch_node(tt2))	#Hello World!

print(bootstrap_dispatcher.state.context['tp2'].dispatch_node(123))


# from efforting.mvp6.abc_factory import ugly_stats

# for key, count in sorted(ugly_stats.items(), key=lambda i: i[1]):
# 	print(count, key)