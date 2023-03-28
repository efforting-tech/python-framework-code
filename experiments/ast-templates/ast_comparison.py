#TODO - put this somewhere in the library perhaps?





def ast_compare(t1, t2, path=()):
	if t1 == t2:
		pass

	elif t1.__class__ is t2.__class__:

		match t1:
			case ast.AST():
				for (field, f1_value) in ast.iter_fields(t1):
					ast_compare(f1_value, getattr(t2, field), path + (field,))

			case list():
				if len(t1) == len(t2):
					for index, (f1_value, f2_value) in enumerate(zip(t1, t2)):
						ast_compare(f1_value, f2_value, path+(index,))

				else:
					print(ast_list_difference(path, t1, t2))

			case str() | float() | int() | bool() | None:
				print(ast_primitive_difference(path, t1, t2))

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')


	else:
		print(ast_tree_difference(path, t1, t2))

class ast_abstract_difference(public_base, abstract=True):
	path = RTS.positional()
	subject = RTS.positional()
	object = RTS.positional()

class ast_primitive_difference(ast_abstract_difference):
	pass

class ast_list_difference(ast_abstract_difference):
	pass

class ast_tree_difference(ast_abstract_difference):
	pass
