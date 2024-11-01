from . import Tokenization_Result, A, Literal_Match, Tokenization_Specifier, Include_Tokenizer, Rule
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



class implemented_tokenizer(R.Record):
	sub_tokenizers: R.Field()
	main: R.Field()


	def tokenize(self, text, start=0, strict=True):
		result = Tokenization_Result(text, start)
		state = tokenization_state(self, result, text)

		sub_tokenizer = state.sub_tokenizer = self.sub_tokenizers[self.main]
		token_stream = Switchable_Iterator(String_Interface.regex_tokenize(text, sub_tokenizer.tokens, start))
		state.token_stream = token_stream


		for token in token_stream:

			print(token)

			action = state.action = state.sub_tokenizer.actions[token.token]
			state.token = token
			action.process(state)
			result.end = token.match.end()

		result.finalized = len(state.tokenizer_stack) == 0
		if strict and not result.finalized:
			raise Exception()

		return result


class implemented_sub_tokenizer(R.Record):
	tokens: R.Field()
	actions: R.Field()


class tokenization_state(R.Record):
	tokenizer: R.Field()
	result: R.Field()
	text: R.Field()
	sub_tokenizer: R.Field()
	token_stream: R.Field()
	action: R.Field()
	token: R.Field()
	tokenizer_stack: R.Field(factory=Stack)
	return_event_stack: R.Field(factory=Stack)

	def push_on_return_event_callback(self, callback):
		self.return_event_stack.push(callback)

	def push_tokenizer(self, sub_tokenizer):
		self.tokenizer_stack.push(self.sub_tokenizer)
		self.sub_tokenizer = sub_tokenizer

	def pop_tokenizer(self):
		self.sub_tokenizer = self.tokenizer_stack.pop()

class implemented_action(R.Record):
	pass

class enter_tokenizer(implemented_action):
	tokenizer: R.Field()

	def process(self, state):
		state.push_tokenizer(state.tokenizer.sub_tokenizers[self.tokenizer])
		state.token_stream.source = String_Interface.regex_tokenize(state.text, state.sub_tokenizer.tokens, state.token.match.end())


class wrapped_chain_tokenizer(implemented_action):
	tokenizer: R.Field()
	wrapper: R.Field()

	def process(self, state):

		def finished_chain(result):
			#todo - pop-tokenizer here
			print('RESULT!', result)
			exit()

		state.push_on_return_event_callback(finished_chain)
		#present_text_with_marker(state.text, state.result.end)

		state.push_tokenizer(state.tokenizer.sub_tokenizers[self.tokenizer])
		state.token_stream.source = String_Interface.regex_tokenize(state.text, state.sub_tokenizer.tokens, state.token.match.end())



class emit_value(implemented_action):
	value: R.Field()

	def process(self, state):
		value = self.value.process(state)
		state.result.emit(value)


class wrap_value(implemented_action):
	wrapper: R.Field()

	def process(self, state):
		value = self.wrapper(state.token.match.group())
		return value

class raise_exception(implemented_action):
	exception: R.Field()

	def process(self, state):
		raise Exception(f'{self.exception}: {state}')

class return_from_tokenizer(implemented_action):

	@staticmethod
	def process(state):
		state.pop_tokenizer()
		state.token_stream.source = String_Interface.regex_tokenize(state.text, state.sub_tokenizer.tokens, state.token.match.end())


def create_action(action):
	match action:
		case A.Enter_Tokenizer(target):
			return enter_tokenizer(target.name)

		case A.Wrapped_Chain_Tokenizer(target, wrapper):
			return wrapped_chain_tokenizer(target.name, wrapper)

		case A.Emit(value):
			return emit_value(create_action(value))

		case A.Wrap(wrapper):
			return wrap_value(wrapper)

		case _ if action is A.Raise_Exception:
			return raise_exception('Unspecified Exception')

		case _ if action is A.Return:
			return return_from_tokenizer

		case unhandled:
			raise Exception(action)

def create_token(condition):
	match condition:
		case Literal_Match(value):
			return re.compile(re.escape(value))

		case unhandled:
			raise Exception(condition)


def Implement_Tokenizer(tokenizers_to_process):
	result = dict()
	main = None
	for tokenizer in tokenizers_to_process:
		pending_tokens = list()
		pending_actions = list()
		for rule in tokenizer.rules:
			pending_tokens.append(create_token(rule.condition))
			pending_actions.append(create_action(rule.action))

		if tokenizer.default_action:
			pending_tokens.append(None)
			pending_actions.append(create_action(tokenizer.default_action))

		# if tokenizer.chain:
		# 	pending_tokens.append(None)
		# 	pending_actions.append(process_chain(tokenizer.chain))


		sub_tokenizer = result[tokenizer.name] = implemented_sub_tokenizer(pending_tokens, pending_actions)
		if not main:
			main = tokenizer.name

	return implemented_tokenizer(result, main)



# def compute_dependencies(target, dependency_graph):
# 	match target:
# 		case Tokenization_Specifier():

# 			if target not in dependency_graph:
# 				dependency_graph[target] = set()

# 				yield target
# 				for rule in target.rules:
# 					for dependency in compute_dependencies(rule, dependency_graph):
# 						print(dependency, '→', target)
# 						dependency_graph[target].add(dependency)

# 				for dependency in compute_dependencies(target.wrapper, dependency_graph):
# 					print(dependency, '→', target)
# 					dependency_graph[target].add(dependency)

# 		case Include_Tokenizer(tokenizer):
# 			yield from compute_dependencies(tokenizer, dependency_graph)

# 		case Rule():
# 			yield from compute_dependencies(target.action, dependency_graph)

# 		case _ if target in (None, A.Return, A.Raise_Exception):
# 			pass

# 		case A.Enter_Tokenizer(target=tokenizer):
# 			tuple(compute_dependencies(tokenizer, dependency_graph))

# 		case unhandled:
# 			raise Exception(target)





# def iter_references(target):

# 	match target:
# 		case Tokenization_Specifier():
# 			yield ('>', target)
# 			for rule in target.rules:
# 				yield from iter_references(rule)

# 			yield from iter_references(target.wrapper)

# 			yield ('<', target)

# 		case Include_Tokenizer(tokenizer):
# 			yield from iter_references(tokenizer)

# 		case Rule():
# 			yield from iter_references(target.action)

# 		case _ if target in (None, A.Return, A.Raise_Exception):
# 			pass

# 		case A.Enter_Tokenizer(target=tokenizer):
# 			yield from iter_references(tokenizer)

# 		case unhandled:
# 			raise Exception(target)


# def compute_dependencies(target):

# 	for ref in iter_references(target):
# 		print(ref)



class dependency_computer(R.Record):
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

			yield item.target

			for sub_item in rev_dep.get(item, ()):
				yield from dependency_order(sub_item)

		def assert_no_cycles(item, previous):
			if item in previous:
				cycle = ' → '.join(t.target.name for t in (*previous, item))
				raise Exception(f'Cycle detected between tokenizers: {cycle}')

			previous[item] = True
			for p in include_map[item]:
				assert_no_cycles(p, previous)

		for leaf in self.get_leaf_references():
			assert_no_cycles(leaf, dict())
			yield from dependency_order(leaf)


	# def assert_no_cycles(self, item, previous):
	# 	print('ITEM', item.target.name, 'PREV', *(p.target.name for p in previous))


		# if item in previous:
		# 	print('CYCLE DETECTED', item.target.name)
		# previous.add(item)

		# for sub_item in rev_dep.get(item, ()):
		# 	assert_no_cycles(sub_item, previous)



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

			case unhandled:
				raise Exception(item)





def Implement_Tokenizer2(tokenizer):

	r = dependency_computer.compute_dependencies(tokenizer)
	for i in r.compute_implementation_order():
		print(i)

	# exit()

	# print(*(i.name for i in r.get_all()))
	# print()


	# for a, b in r.iter_dependencies():
	# 	print(a.name, b.name)




	#print()
	#for key, value in dg.items():
		#print(key.name, *sorted(v.name for v in value))


	#This is not correct
	# TODO we need to find a way to resolve the dependency graph


	# print()

	# deps = set()
	# for v in dg.values():
	# 	deps |= v

	# all = set(dg.keys()) | deps
	# free = all - deps

	# print('all', sorted(v.name for v in all))
	# print('free', sorted(v.name for v in free))