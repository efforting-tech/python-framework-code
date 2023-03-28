import ast

class extended_ast_node_transformer(ast.NodeTransformer):
	previous_sibling = None

	def generic_visit(self, node):
		#Will make sure previous_sibling is updated
		for field, old_value in ast.iter_fields(node):
			if isinstance(old_value, list):
				new_values = []
				self.previous_sibling = None
				for value in old_value:
					pending_sibling = value
					if isinstance(value, ast.AST):
						value = self.visit(value)
						self.previous_sibling = pending_sibling
						if value is None:
							continue
						elif not isinstance(value, ast.AST):
							new_values.extend(value)
							continue
					new_values.append(value)
				old_value[:] = new_values
			elif isinstance(old_value, ast.AST):
				new_node = self.visit(old_value)

				#Expressions get special treatment so we may remove them or expand them
				if isinstance(node, ast.Expr):
					if new_node is None:
						return	#We are removing this entire Expr node
					elif isinstance(new_node, ast.Expr):	#Unpack inner expression
						return new_node
					elif isinstance(new_node, ast.AST):
						node.value = new_node	#Update this expression
					else:
						return new_node	#This is probably a sequence, return it

				elif new_node is None:
					delattr(node, field)
				else:
					setattr(node, field, new_node)

		#Fill in pass when needed
		if 'body' in node._fields and not node.body:
			node.body.append(ast.Pass())

		return node
