from efforting.mvp4.presets.text_processing import *
import ast
FROM_TOKENIZER = object()	#TODO - symbol

# local_template_context = template_context(
# 	update_linecache = True,
# 	tokenizer = custom_template_tokenizer(
# 		'{', 		#Expression ingress
# 		'}', 		#Expression egress

# 		#Find		Replace with	(escape sequences)
# 		'{{', 		'{',
# 		'}}', 		'}',
# 	),
# )


template_tokenizer = custom_template_tokenizer(
	'{', 		#Expression ingress
	'}', 		#Expression egress

	#Find		Replace with	(escape sequences)
	'{{', 		'{',
	'}}', 		'}',
)



# class local_template_renderer(simple_template_renderer):
# 	fields = RTS.state()

# 	def render_expression(self, expression):
# 		return self.fields[expression]

# 	def render(self, tree, **named):
# 		with attribute_stack(self, fields=named):
# 			return self.transform_tree(tree)

UNDEFINED = object() #TODO symbol

class template_field(public_base):
	name = RTS.positional()
	positional = RTS.field(default=True)
	default = RTS.field(default=UNDEFINED)

class local_template(simple_template_renderer):
	#DERIVED simple_template_renderer.name
	#DERIVED simple_template_renderer.tokenizer
	body = RTS.positional()
	fields = RTS.positional()
	replacements = RTS.state()

	@RTS.initializer
	def initial_field_processing(self):
		#for f in self.fields:
		new_fields = dict()
		for f in self.fields:
			match f.split(maxsplit=2):
				case ['named', field, default]:
					new_fields[field] = template_field(field, False, ast.literal_eval(default))
				case ['named', field]:
					new_fields[field] = template_field(field, False)
				case [field]:
					new_fields[field] = template_field(field)
				case _:
					raise Exception(f)


		self.fields = new_fields

	#@RTS.cached_property(fields)		Future
	@property
	def positional_fields(self):
		return tuple(f for f in self.fields.values() if f.positional)

	@property
	def named_fields(self):
		return tuple(f for f in self.fields.values() if not f.positional)

	def render_expression(self, expression):
		#Note - this should have been prerendered so that we only parse fields once (maybe we could have a transfer function for expressions later in the simple_template_renderer (yes, do this!))

		match expression.split(maxsplit=2):
			case ['named', field_name, default]:
				pass
			case ['named', field_name]:
				pass
			case [field_name]:
				pass
			case _:
				raise Exception(f)

		field = self.fields[field_name]
		MISS = object()	#TODO - symbol
		if (value := self.replacements.get(field_name, MISS)) is not MISS:
			return value

		if field.default is not UNDEFINED:
			return field.default
		else:
			raise Exception(field)

	def render(self, *positional, **named):

		replacements = {field.name: value for field, value in zip(self.positional_fields, positional)}
		replacements.update({self.fields[field_name].name: value for field_name, value in named.items()})	#This lookup ensures we use existing fields

		with attribute_stack(self, replacements=replacements):
			return self.transform_tree(self.body)

	@classmethod
	def from_text(cls, tokenizer, text, name=None, fields=FROM_TOKENIZER):
		body = text_node.from_text(text)
		if fields is FROM_TOKENIZER:
			fields = list()
			for item in tokenizer.tokenize(body.text):
				match item:
					case token_match(match=match) if item.classification is TC.CL.expression:
						fields.append(match)

		return cls(name, tokenizer, body, fields)

	@classmethod
	def from_path(cls, tokenizer, path, name=None, fields=FROM_TOKENIZER):
		body = text_node.from_path(path)
		if fields is FROM_TOKENIZER:
			fields = list()
			for item in tokenizer.tokenize(body.text):
				match item:
					case token_match(match=match) if item.classification is TC.CL.expression:
						fields.append(match)

		return cls(name, tokenizer, body, fields)



class file_resource_renderer(public_base):
	path = RTS.positional()
	name = RTS.field(default=None)
	preload = RTS.field(default=True)
	tokenizer = RTS.setting(template_tokenizer)

	template = RTS.state(default=None)
	last_change = RTS.state(default=None)

	def preview(self):
		self.reload_if_needed()
		return self.render(**{f: f'→ {f} ←' for f in self.template.fields})

	def render(self, *positional, **named):
		self.reload_if_needed()
		return self.template.render(*positional, **named)


	@RTS.initializer
	def check_preload(self):
		if self.preload:
			self.reload_if_needed()

	def reload_if_needed(self):
		p = Path(self.path)
		lc = p.stat().st_mtime
		if self.last_change is None or lc > self.last_change:
			self.last_change = lc
			self.template = local_template.from_text(self.tokenizer, p.read_text(), self.name)





