from ... import record as R
from ..tree_view import Tree_View_Dispatcher
from . import patterns as MP
from ...text import Mutable_Tree_View

#Create the core dispatcher
class Mnemonic_Core_Dispatcher(R.Record):
	global_context_setup: 	R.Field(factory=list)
	local_context_setup: 	R.Field(factory=list)
	result:				 	R.Field(factory=dict)

	D = Tree_View_Dispatcher()

	def dispatch_tree(self, tree):
		return self.D.bound_dispatch_tree(self, tree)

	@D.register(MP.terminal, 'core tree translation global context setup')
	def core_tree_translation_global_context_setup(self, dispatcher, node, result):
		self.global_context_setup.append(node.body.normal())

	@D.register(MP.terminal, 'core tree translation local context setup')
	def core_tree_translation_local_context_setup(self, dispatcher, node, result):
		self.local_context_setup.append(node.body.normal())

	@D.register(MP.terminal, 'core tree translation map')
	def core_tree_translation_map(self, dispatcher, node, result):

		dispatcher_defs = Mutable_Tree_View()
		rule_defs = Mutable_Tree_View()
		export = set()

		for sub_dispatcher_node in node.body.iter_nodes():
			dispatcher_defs.write_line(f'{sub_dispatcher_node.title} = Tree_View_Dispatcher()')
			export.add(sub_dispatcher_node.title)

			for line in sub_dispatcher_node.body.lines:
				pattern, expression = map(str.strip, line.value.split('→'))

				rule_defs.write_line(f'@{sub_dispatcher_node.title}.register({pattern})')
				rule_defs.write_line(f'def handler(dispatcher, node, result):')
				rule_defs.write_pieces(self.local_context_setup, indent_adjustment=1)
				rule_defs.write_line(f'\treturn {expression}')
				rule_defs.write_line()

		dispatcher_defs.write_line()

		code_tree = Mutable_Tree_View()

		code_tree.write_pieces(self.global_context_setup)
		code_tree.write_line()
		code_tree.write_pieces((
			dispatcher_defs,
			rule_defs,
		))

		scope = dict(
			Tree_View_Dispatcher = Tree_View_Dispatcher,
		)

		exec(code_tree.to_str(), scope)

		self.result.update({name: item for name, item in scope.items() if name in export})
