from t1 import *
import sys, inspect



class test_transformer(ast.NodeTransformer):

	def visit(self, item):
		if isinstance(item, list):
			result = list()
			for sub_item in item:

				match sub_item:
					case ast.FunctionDef(name=name):
						print(name, sub_item)
						result.append(self.visit(sub_item))
						result.append(assign.render_ast(ast.Name(name, ast.Load()), ast.Constant(sub_item)))
					case _:
						result.append(self.visit(sub_item))

			return result

		else:
			return super().visit(item)


def transform_node(node):
	match node:
		case ast.AST() as tree:
			args = ', '.join(transform_node(value) for (field, value) in ast.iter_fields(tree))
			return f'ast.{tree.__class__.__qualname__}({args})'

		case list() as sequence:
			inner = ', '.join(map(transform_node, sequence))
			return f'[{inner}]'

		case text_place_holder(id=ph):
			return ph

		case str() | float() | int() | bool() | None:
			return repr(node)

		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')


#Experiment

assign = ast_template(r'''

	class {name}({*bases}):
		{doc}

		def __init__(self):
			print('Hello World!')

''')

assign = ast_template(r'''

	if {name} is DEFAULT:
		{name} = cls.{name}.default

''')


print(transform_node(assign.tree))

#print(ast_template('def stuff(a, b):\n\tpass').tree.args._fields)


def maybe_assign(name):
	return ast.If(ast.Compare(ast.Name(name), [ast.Is()], [ast.Name('DEFAULT', ast.Load())]), [ast.Assign([ast.Name(name)], ast.Attribute(ast.Name('self', ast.Load()), name, ast.Load()), None)], [])


def classmethod_with_settings(f):

	settings = set()
	for name, value in sys._getframe(1).f_locals.items():
		if isinstance(value, RTS.field):
			if value.field_type is RTS.SETTING:
				settings.add(name)

	signature = inspect.signature(f)

	new_args = list()
	defaults = list()
	function_body = ast.parse(textwrap.dedent(inspect.getsource(f))).body[0].body

	for name, parameter in signature.parameters.items():
		if name in settings:
			assert parameter == inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD)	#This assertion makes sure the parameter is a regular one
			#new_args.append(f'{name}=DEFAULT')
			new_args.append(ast.arg(name))
			defaults.append(ast.Name('DEFAULT'))
			function_body.insert(0, maybe_assign(name))

		else:
			pass
			new_args.append(ast.arg(name))
			#new_args.append(parameter)


	tree = ast.FunctionDef(f.__name__, ast.arguments([], new_args, None, [], [], None, defaults), function_body, [])






@classmethod_with_settings
def test_template(name, bases, doc):
	#This is the output from transform_node above
	return ast.ClassDef(name, [*bases], [], [
		ast.Expr(doc),
		ast.FunctionDef('__init__', ast.arguments([], [ast.arg('self', None, None)], None, [], [], None, []), [
			ast.Expr(ast.Call(ast.Name('print', ast.Load()), [ast.Constant('Hello World!', None)], []))
		], [], None, None)
	], [])

# cd = test_template('mah_class', (ast.Name('some_base'), ast.keyword('some_attribute', ast.Constant('some setting'))), ast.Constant('Here be docs!'))


# print()
# print(unparse_ast(cd))

# Output

# class mah_class(some_base, some_attribute='some setting'):
#     """Here be docs!"""

#     def __init__(self):
#         print('Hello World!')



class table(public_base):
	columns = RTS.optional_factory(tuple)
	rows = RTS.optional_factory(list)

	tab_size = RTS.setting(4)
	min_raster_spacing = RTS.setting(3, description='Minimum spacing required to separate headers in a raster table')
	strip_raster_cells = RTS.setting(True)


	@classmethod_with_settings
	def from_raster(cls, text, tab_size, min_raster_spacing, strip_raster_cells):
		print('Settings are', tab_size, min_raster_spacing, strip_raster_cells)
