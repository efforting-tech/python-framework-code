from package_introspection import load_package #TODO - should be moved to library
import ast

from efforting.mvp6.core import record as R

from importlib.util import find_spec

class abstract_import_statement(R.Record):
	name: R.Field()
	top_level: R.Field()

class absolute_import(abstract_import_statement):
	pass

class unresolved_import(abstract_import_statement):
	pass




class import_visitor(ast.NodeVisitor):
	def visit_Module(self, node):
		self.top_level_nodes = set(node.body)
		self.result = list()
		self.generic_visit(node)

	def visit_Import(self, node):
		for name in node.names:
			self.result.append(absolute_import(name.name, node in self.top_level_nodes))
		self.generic_visit(node)

	def visit_ImportFrom(self, node):
		#print('  ', node, node in self.top_level_nodes)

		#print(node.__getstate__())


		for name in node.names:
			#self.result.append(absolute_import(name.name, node in self.top_level_nodes))

			if node.level == 0:
				#print(f'from {node.module} import {name.name}')
				for candidate in (f'{node.module}.{name.name}', f'{node.module}'):
					try:
						if find_spec(candidate):
							self.result.append(absolute_import(candidate, node in self.top_level_nodes))
							break
					except:
						pass
				else:
					self.result.append(unresolved_import(candidate, node in self.top_level_nodes))

			else:

				if node.module:
					if node.level == 1:
						module = self.module_path[:-node.level] + node.module.split('.')
					else:
						module = self.module_path[:-node.level] + node.module.split('.')
				else:
					module = self.module_path[:]

				module_path = '.'.join(module)
				#print(node.level, node.module, self.module_path, module)

				for candidate in (f'{module_path}.{name.name}', module_path):
					try:
						if find_spec(candidate):
							self.result.append(absolute_import(candidate, node in self.top_level_nodes))
							break
					except:
						pass
				else:
					self.result.append(unresolved_import(candidate, node in self.top_level_nodes))



		self.generic_visit(node)

def get_imports(library):
	v = import_visitor()
	v.module_path = library.full_name.split('.')
	v.visit(library.ast)
	return v.result






mermaid_intro = '''
graph TD
	classDef module fill:#f9f,stroke:#333,color:#000,stroke-width:2px;
	classDef unresolved_module fill:#f96,stroke:#333,color:#000,stroke-width:2px;
	linkStyle default stroke:#1f77b4,stroke-width:2px,stroke-line: 5,5;
'''

print(mermaid_intro)

'''
    moduleA["Module A"]:::module --> moduleB["Module B"]:::module
    moduleB --> unresolvedModuleA["Unresolved Module A"]:::unresolved_module

    moduleA -.-> unresolvedModuleB["Unresolved Module B"]:::unresolved_module
    unresolvedModuleA -.-> moduleC["Module C"]:::module
'''



pkg = load_package('efforting.mvp6')
pkg.initialize()
for name in sorted(pkg.registry):

	# if name != 'efforting.mvp6.state_machine':
	# 	continue

	module = pkg.registry[name]


	#print(module.full_name)
	for item in get_imports(module):
		#print('   ', item)
		match item:
			case absolute_import(name, top_level=top_level):
				link = '-->' if top_level else '-.->'
				#print(f'	{module.full_name}:::module --> {name}:::module')

			case unresolved_import(name, top_level=top_level):
				link = '-->' if top_level else '-.->'
				print(f'	{module.full_name}:::module {link} {name}:::unresolved_module')

