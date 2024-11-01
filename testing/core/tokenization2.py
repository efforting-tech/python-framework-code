#from efforting.mvp6.core.data_conditions import record as DC

#These are just some sketching for now


# def create_rules_to_tokenization_dict():

# 	result = Translator()	#TODO - support naming

# 	condition_translator = Translator()	#TODO - support naming

# 	@condition_translator.register_function(DC.Instance_of(Literal_Match))
# 	def handle_literal_match(condition):
# 		return re.compile(re.escape(condition.value))

# 	@result.register_function(DC.Instance_of(Rule))
# 	def handle_rule(rule):
# 		return condition_translator.dispatch_item(rule.condition), rule.action


# 	return result

#rules_to_tokenization_dict = create_rules_to_tokenization_dict()


# @functools.cache
# def default_implementation_factory(specification):

# 	rules = dict(rules_to_tokenization_dict.dispatch_sequence(specification.rules))
# 	if specification.default_action:
# 		rules[None] = specification.default_action

# 	patterns, actions = zip(*rules.items())

# 	return Regex_Tokenizer(specification, patterns, actions)



# class Regex_Tokenizer(R.Record):
# 	specification: R.Field()
# 	patterns: R.Field()
# 	actions: R.Field()


# def create_default_action_handler():
# 	result = Single_Operation_Processor()

# 	@result.register_function(DC.Instance_of(A.Emit))
# 	def process_emit(tokenizer, item):
# 		print(result.bound_dispatch_item(tokenizer, item.value))

# 	@result.register_function(DC.Instance_of(A.Wrap))
# 	def process_wrap(tokenizer, item):
# 		print(item)
# 		exit()

# 	return result

# default_action_handler = create_default_action_handler()



# class Tokenize(R.Record):
# 	pending_specification: R.Field()
# 	text: R.Field()
# 	position: R.Field(default=0)

# 	implementation_factory: R.Field(default=default_implementation_factory)
# 	action_handler: R.Field(default=default_action_handler)

# 	def __iter__(self):
# 		implementation = self.implementation_factory(self.pending_specification)

# 		for token in String_Interface.regex_tokenize(self.text, implementation.patterns, self.position):
# 			action = implementation.actions[token.token]

# 			self.action_handler.bound_dispatch_item(self, action)

# 			print(token, action)

# 		yield from ()


