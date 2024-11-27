from . import Tokenization_Result, A, Literal_Match, Tokenization_Specifier, Include_Tokenizer, Rule, Match_Anything, Regex_Match
from ... import record as R
from ....iteration import Switchable_Iterator
from ....str.interface import String_Interface
from ...data import Stack, Data_Stack, Identity_Reference
import re
from collections import defaultdict

#TODO - move this function
def present_text_with_marker(text, pos):
	real_pos = 1 + len(repr(text[:pos])) - 2
	print(repr(text))
	indent = real_pos * ' '
	print(f'{indent}↑')




class Implemented_Rule(R.Record):
	condition: R.Field()
	action: R.Field()


class Dependency_Computer(R.Record):
	#stack: R.Field(factory=R.Bound_Factory(Context_Stack))
	tokenizer: R.Field() = None
	seen: R.Field(factory=set)
	root_branches: R.Field(factory=set)
	dependencies: R.Field(factory=set)
	includes: R.Field(factory=set)


	def stack(self, *positional, **named):
		return Data_Stack(self, *positional, **named)

	@classmethod
	def compute_dependencies(cls, target):
		result = cls()
		result.feed(target)
		return result

	def iter_dependencies(self):
		for a, b in self.dependencies:
			yield a.target, b.target

	def get_all(self):
		resulting_set = set(self.root_branches)
		for a, b in self.dependencies:
			resulting_set |= {a, b}

		return tuple(i.target for i in resulting_set)

	def get_root_branches(self):
		resulting_set = set(self.root_branches)
		return tuple(i.target for i in resulting_set)

	def get_leaves(self):
		resulting_set = set(self.root_branches)
		for a, b in self.dependencies:
			resulting_set.add(b)

		for a, b in self.dependencies:
			resulting_set.discard(a)

		return tuple(i.target for i in resulting_set)

	def get_leaf_references(self):
		resulting_set = set(self.root_branches)
		for a, b in self.dependencies:
			resulting_set.add(b)

		for a, b in self.dependencies:
			resulting_set.discard(a)

		return resulting_set


	def compute_implementation_order(self):
		rev_dep = defaultdict(set)
		include_map = defaultdict(set)
		seen = set()

		for a, b in self.dependencies:
			rev_dep[b].add(a)

		for a, b in self.includes:
			include_map[a].add(b)

		def dependency_order(item):
			if item in seen:
				return

			seen.add(item)

			for sub_item in include_map.get(item, ()):
				yield from dependency_order(sub_item)

			yield item.target

		def assert_no_cycles(item, previous):
			if item in previous:
				#TODO - should cut from first occurance of "item"
				cycle = ' → '.join(t.target.name for t in (*previous, item))
				raise Exception(f'Cycle detected between tokenizers: {cycle}')

			previous[item] = True
			for p in include_map[item]:
				assert_no_cycles(p, previous)

		for b in self.root_branches:
			for entry in dependency_order(b):
				assert_no_cycles(entry, dict())
				yield entry



	def feed(self, item):
		id_ref = Identity_Reference(item)
		if id_ref in self.seen:
			return

		self.seen.add(id_ref)

		match item:
			case Tokenization_Specifier():
				if self.tokenizer:
					self.dependencies.add((self.tokenizer, id_ref))
				else:
					self.root_branches.add(id_ref)

				with self.stack(tokenizer=id_ref):
					for rule in item.rules:
						self.feed(rule)
					self.feed(item.wrapper)


			case Include_Tokenizer(tokenizer):
				self.includes.add((self.tokenizer, Identity_Reference(tokenizer)))
				self.feed(tokenizer)

			case Rule():
				self.feed(item.action)

			case _ if item in (None, A.Return, A.Raise_Exception):
				pass

			case A.Enter_Tokenizer(target=tokenizer):
				with self.stack(tokenizer=None):
					self.feed(tokenizer)

			case A.Emit(value=value):
				self.feed(value)

			case A.Wrap():
				pass


			case unhandled:
				raise Exception(item)





#TODO - maybe move the MVP stuff to its own place?

class MVP_Action(R.Record):
	pass

class MVP_Enter_Tokenizer(MVP_Action):
	tokenizer: R.Field()
	wrapper: R.Field() = None
	unpack: R.Field() = False

	def process(self, state):
		state.push_tokenizer(self.tokenizer)
		state.push_result_tokens([])
		state.push_wrapper(self.wrapper)
		state.push_unpack(self.unpack)
		state.token_stream.source = String_Interface.regex_tokenize(state.text, state.sub_tokenizer.tokens, state.token.match.end())

class MVP_Emit_Value(MVP_Action):
	value: R.Field()

	def process(self, state):
		value = self.value.process(state)
		state.result.emit(value)

class MVP_Wrap_Value(MVP_Action):
	wrapper: R.Field()

	def process(self, state):
		value = self.wrapper(state.token.match.group())
		return value

class MVP_Wrap_Match(MVP_Action):
	wrapper: R.Field()

	def process(self, state):
		value = self.wrapper(state.token.match)
		return value

class MVP_Raise_Exception(MVP_Action):
	exception: R.Field()

	def process(self, state):
		#Now we just assume self.exception is a string but we may have it be a type or factory later
		raise Exception(f'Exception {self.exception!r} when encountering {state.token} on line {state.source}')

		# print(state.result.end)
		# print(state.token)
		# raise NotImplementedError
		# raise Exception(f'{self.exception}: {state}')

#TODO - I think we should have a better way for no data actions - Possibly akin to a derived symbol?
#		In the end we probably want something that behaves like a singleton

#TODO - We need to figure out a good way of adding tracking information, maybe as a side channel

class MVP_Return_From_Tokenizer(MVP_Action):
	@staticmethod
	def process(state):
		state.pop_tokenizer()
		result_tokens = state.pop_result_tokens()

		if wrapper := state.pop_wrapper():
			result_tokens = wrapper(result_tokens)

		if state.unpack:
			state.result.tokens.extend(result_tokens)
		else:
			state.result.tokens.append(result_tokens)

		state.token_stream.source = String_Interface.regex_tokenize(state.text, state.sub_tokenizer.tokens, state.token.match.end())


class MVP_Sub_Tokenizer(R.Record):
	source_spec: R.Field()
	source_rules: R.Field()
	tokens: R.Field()
	actions: R.Field()
	#default_action: R.Field() = None



class MVP_Tokenizer_Factory(R.Record):
	lut_rules_by_spec: R.Field(factory=dict)
	lut_acceleration_structure_by_spec: R.Field(factory=dict)
	lut_acceleration_structure_by_name: R.Field(factory=dict)
	ingress: R.Field() = None

	@classmethod
	def implement_tokenizer(cls, top):
		factory = cls()

		r = Dependency_Computer.compute_dependencies(top)
		implo = r.compute_implementation_order()

		#Step 1 - Collate rules
		for spec in implo:
			factory.lut_rules_by_spec[spec] = list()
			for rule in spec.rules:
				implemented_rules = factory.implement_rules(rule)
				factory.lut_rules_by_spec[spec].extend(implemented_rules)


			if spec.default_action:
				factory.lut_rules_by_spec[spec].append(Implemented_Rule(Match_Anything, factory.implement_action(spec.default_action)))


		#Step 2 - Create acceleration structures
		for spec, rules in factory.lut_rules_by_spec.items():
			factory.lut_acceleration_structure_by_name[spec.name] = factory.lut_acceleration_structure_by_spec[spec] = factory.create_acceleration_structure_for_rules(spec, rules)


		for acceleration_structure in factory.lut_acceleration_structure_by_spec.values():
			#Post processing
			acceleration_structure.tokens = tuple(acceleration_structure.tokens)
			acceleration_structure.actions = tuple(map(factory.resolve_action, acceleration_structure.actions))


		#Step 3 - Finalize
		factory.ingress = factory.lut_acceleration_structure_by_spec[top]
		return factory


	def create_acceleration_structure_for_rules(self, spec, rules):

		result = MVP_Sub_Tokenizer(spec, rules)

		regular_rules = [r for r in rules if r.condition is not Match_Anything]
		default_rules = [r for r in rules if r.condition is Match_Anything]

		result.tokens = [r.condition for r in regular_rules]
		result.actions = [r.action for r in regular_rules]

		match default_rules:
			case []:
				pass

			case [default_rule]:
				#result.default_action = default_rule.action
				result.tokens.append(None)
				result.actions.append(default_rule.action)

			case unhandled:
				raise Exception(default_rules)

		return result


	def resolve_action(self, action):
		match action:

			case MVP_Enter_Tokenizer(tokenizer, wrapper, unpack):
				return MVP_Enter_Tokenizer(self.lut_acceleration_structure_by_name[tokenizer], wrapper, unpack)

			case MVP_Emit_Value(value):
				return MVP_Emit_Value(self.resolve_action(value))

			case MVP_Wrap_Value() | MVP_Wrap_Match() | MVP_Raise_Exception():
				return action

			case _ if action is MVP_Return_From_Tokenizer:
				return action

			case unhandled:
				raise Exception(unhandled)

	def create_tokens(self, source):
		match source:
			case Literal_Match(value):
				return re.compile(re.escape(value))

			case Regex_Match(value):
				return re.compile(value)

			case unhandled:
				raise Exception(unhandled)

	def implement_action(self, source):
		match source:
			case A.Enter_Tokenizer(target, wrapper=wrapper, unpack=unpack):
				return MVP_Enter_Tokenizer(target.name, wrapper=wrapper, unpack=unpack)

			case A.Wrapped_Chain_Tokenizer(target, wrapper):
				return wrapped_chain_tokenizer(target.name, wrapper)

			case A.Emit(value):
				return MVP_Emit_Value(self.implement_action(value))

			case A.Wrap(wrapper):
				return MVP_Wrap_Value(wrapper)

			case A.Wrap_Match(wrapper):
				return MVP_Wrap_Match(wrapper)

			case _ if source is A.Raise_Exception:
				return MVP_Raise_Exception('Unspecified Exception')

			case _ if source is A.Return:
				return MVP_Return_From_Tokenizer

			case unhandled:
				raise Exception(source)


	def implement_rules(self, source):
		#Returns lists of rules since certain rules include other rules
		match source:
			case Rule():
				return [Implemented_Rule(self.create_tokens(source.condition), self.implement_action(source.action))]

			case Include_Tokenizer(spec):
				return self.lut_rules_by_spec[spec]

			case unhandled:
				raise Exception(unhandled)



	def tokenize(self, text, start=0, strict=True, source=None):
		result = Tokenization_Result(text, start)
		state = Tokenization_State(self, result, text, self.ingress, source)

		token_stream = Switchable_Iterator(String_Interface.regex_tokenize(text, state.sub_tokenizer.tokens, start))
		state.token_stream = token_stream

		for token in token_stream:
			action = state.action = state.sub_tokenizer.actions[token.token]
			state.token = token
			action.process(state)
			result.end = token.match.end()

		result.finalized = len(state.tokenizer_stack) == 0
		if strict and not result.finalized:
			raise Exception()

		return result



class Tokenization_State(R.Record):
	tokenizer: R.Field()
	result: R.Field()
	text: R.Field()
	sub_tokenizer: R.Field()
	source: R.Field() = None
	wrapper: R.Field() = None
	token_stream: R.Field()
	action: R.Field()
	token: R.Field()
	unpack: R.Field() = False
	tokenizer_stack: R.Field(factory=Stack)
	wrapper_stack: R.Field(factory=Stack)
	unpack_stack: R.Field(factory=Stack)
	result_tokens_stack: R.Field(factory=Stack)

	#TODO - maybe we can simplify this a bunch and just use the Stack interface
	def push_result_tokens(self, result_tokens):
		self.result_tokens_stack.push(self.result.tokens)
		self.result.tokens = result_tokens

	def pop_result_tokens(self):
		result_tokens = self.result.tokens
		self.result.tokens = self.result_tokens_stack.pop()
		return result_tokens

	def push_tokenizer(self, sub_tokenizer):
		self.tokenizer_stack.push(self.sub_tokenizer)
		self.sub_tokenizer = sub_tokenizer

	def pop_tokenizer(self):
		sub_tokenizer = self.sub_tokenizer
		self.sub_tokenizer = self.tokenizer_stack.pop()
		return sub_tokenizer

	def push_wrapper(self, wrapper):
		self.wrapper_stack.push(self.wrapper)
		self.wrapper = wrapper

	def pop_wrapper(self):
		wrapper = self.wrapper
		self.wrapper = self.wrapper_stack.pop()
		return wrapper


	def push_unpack(self, unpack):
		self.unpack_stack.push(self.unpack)
		self.unpack = unpack

	def pop_unpack(self):
		unpack = self.unpack
		self.unpack = self.unpack_stack.pop()
		return unpack
