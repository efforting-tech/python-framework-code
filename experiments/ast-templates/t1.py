import ast, textwrap
from efforting.mvp4.presets.text_processing import custom_template_tokenizer, TC, RTS, public_base

from uuid import uuid4

def create_multiple_unique_values(count, factory=uuid4):
	result = set()
	while len(result) < count:
		result.add(factory())

	return result


def create_multiple_unique_identifiers(count):
	result = set()
	while len(result) < count:
		result.add(f'_{uuid4()}'.replace('-', '_'))

	return result

def create_unique_identifier(target):
	target_length = len(target) + 1
	while len(target) < target_length:
		candidate = f'_{uuid4()}'.replace('-', '_')
		result.add(candidate)

	return candidate


class text_place_holder(public_base):
	id = RTS.positional()

class simple_text_template(public_base):
	text = RTS.positional()
	tokenizer = RTS.factory(custom_template_tokenizer,
		'{', 		#Expression ingress
		'}', 		#Expression egress

		#Find		Replace with	(escape sequences)
		'{{', 		'{',
		'}}', 		'}',
	)

	template = RTS.factory(list)
	place_holders = RTS.factory(dict)

	@RTS.initializer
	def load_template(self):
		for token in self.tokenizer.tokenize(self.text):
			match token.classification:
				case TC.CL.expression:
					if (ph := self.place_holders.get(token.match)) is None:
						ph = self.place_holders[token.match] = text_place_holder(token.match)
					self.template.append(ph)

				case TC.CL.text:
					match self.template:
						case [*_, str() as last]:
							self.template[-1] += token.match	#Concatenate consequtive text tokens
						case _:
							self.template.append(token.match)

	def render(self, *positional, **named):
		place_holders = dict(zip(self.place_holders, positional), **named)

		result = ''
		for token in self.template:
			match token:
				case str():
					result += token
				case text_place_holder() as ph:
					result += place_holders[ph.id]
				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')

		return result


def ast_template_from_placeholders(value, placeholders):
	match value:
		case ast.Name(id=id) if ph := placeholders.get(id):
			return ph

		case ast.AST() as tree:
			return tree.__class__(*(ast_template_from_placeholders(value, placeholders) for (field, value) in ast.iter_fields(tree)))

		case list() as sequence:
			return [ast_template_from_placeholders(value, placeholders) for value in sequence]

		case str() as key if ph := placeholders.get(key):
			return ph

		case str() | float() | int() | bool() | None:
			return value

		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')





def preview_ast(tree):
	def transform_node(node):
		match node:
			case ast.AST() as tree:
				return tree.__class__(*(transform_node(value) for (field, value) in ast.iter_fields(tree)))

			case list() as sequence:
				return list(map(transform_node, sequence))

			case text_place_holder() as ph:
				return f'`{ph.id}´'

			case str() | float() | int() | bool() | None:
				return node

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	return transform_node(tree)

def render_ast(tree, place_holders):
	def transform_node(node):
		match node:
			case ast.AST() as tree:
				return tree.__class__(*(transform_node(value) for (field, value) in ast.iter_fields(tree)))

			case list() as sequence:
				return list(map(transform_node, sequence))

			case text_place_holder() as ph:
				return place_holders[ph.id]

			case str() | float() | int() | bool() | None:
				return node

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	return transform_node(tree)

def unparse_ast(tree):
	match tree:
		case ast.AST():
			return ast.unparse(ast.fix_missing_locations(tree))
		case list() as sequence:
			return unparse_ast(ast.Module(body=sequence, type_ignores=[]))	#Must be list
		case str() | float() | int() | bool() | None:
			return repr(tree)
		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')



class ast_template(public_base):
	code = RTS.positional()
	tree = RTS.state()
	place_holders = RTS.state()


	@RTS.initializer
	def load_template(self):
		#Note - this method uses an ugly hack for identifying placeholders in the AST
		#		The user must avoid using variables or literals that has the form of `_{uuid4}´

		#Step one - create the text template
		text_template = simple_text_template(textwrap.dedent(self.code))

		#Step two - assign unique values
		ph_map = dict(zip(create_multiple_unique_identifiers(len(text_template.place_holders)), text_template.place_holders.values()))

		tree = ast.parse(text_template.render(*ph_map))
		self.place_holders = text_template.place_holders

		result = ast_template_from_placeholders(tree, ph_map)

		match result:
			case ast.Module(body=[sole_item]):
				self.tree = sole_item
			case _:
				self.tree = result.body


	def render_ast(self, *positional, **named):
		return render_ast(self.tree, dict(zip(self.place_holders, positional), **named))

	def render(self, *positional, **named):
		return unparse_ast(render_ast(self.tree, dict(zip(self.place_holders, positional), **named)))

	def preview(self):
		return unparse_ast(preview_ast(self.tree))

# t = ast_template('''

# 	if {name} is DEFAULT: #{{stuff}}
# 		{name} = self.{name}

# ''')
#print(unparse_ast(t.render('hello')))



# generator = ast_template('({yes} if {condition} else {no} for v in {sequence})')
# condition = ast_template('isinstance({item}, str) and item.startswith({prefix})')

# print(generator.tree.value.elt.test)
# nt = generator.render_ast(ast.Constant('yes'), condition.render_ast(ast.Name('v'), ast.Constant('prefix')).value, ast.Constant('no'), ast.Constant('seq'))

# print(unparse_ast( nt ))

if __name__ == '__main__':


	fdef = ast_template('''
		def some_function():
			item = 123

		def another_function():
			stuff = 123

	''')


	assign = ast_template('{target}.ast = {value}')

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


	t = test_transformer().visit(fdef.tree)
	#This tree can't be unparsed, but can it be compield?

	#We also can't add weird stuff in ast.Constant
	#We should make an AST processing context that can keep track of custom constants and such

	m = ast.Module(body=t, type_ignores=[])
	fm = ast.fix_missing_locations(m)
	#print(fm.body[1])


	c = compile(fm, '<ast>', 'exec')
	exec(c)
	print(some_function.ast)


