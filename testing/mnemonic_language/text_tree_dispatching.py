from efforting.mvp6.processing.dispatcher import Regulations, Dispatcher, regex_rule, sub_dispatcher_rule, generic_data_condition, Rule_Match
from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.mnemonic_language.parser import tp
from efforting.mvp6.mnemonic_language.mnemonic_tokens_to_pattern import mttp
from efforting.mvp6.processing.text_tree import Text_Tree_Dispatcher, Text_Tree_Dispatcher_Action

from efforting.mvp6.mnemonic_language.string_formatting_rules import string_formatter


from efforting.mvp6.mnemonic_language.processing import mnemonic_to_regex
from efforting.mvp6.text.tree import Text_Tree_Listing

from efforting.mvp6.data_view import View_Definition, Field_Conversion_Rule


#NEXT UP - We started with the pattern recognizer and tokens but then we hit a snag here which we can solve but want to put off to later. This means we now mix regex and token pattern matches which we currently solved by using a fallback
#			I would prefer if we used a single regulations object but we had different sub regulations depending on if we should work with the tokens or the strings. I think a reasonable approach here is to have a data view object
#			that can have multiple views and define conversations between views. It can then automatically resolve items.

#NEXT UP - we are back at the inconsistency in who should keep track of the context/processor state. Maybe we should make a processor and leave the regulations outside of it
#			NOTE - after considering it for a bit I think we should have an abstract processor state that supports shallow copy so we can easily copy the state. That way processor can keep regulations and name and only have state instead of a bunch of
#					loose members like we do now
#			TODO - see above note
#			ADDENDUM - we should probably use the context object and stack the contexts

#print(mnemonic_to_regex.process_item('hello world[:] {name as thing}'))
#exit()

test_tree = create_text_tree_document_from_str('''

	amend current processor:
		setup:
			ps.node
			ps.captures as cpt
			ctx.hello
			-dispatcher
			msys.dispatcher as D
			cpt.thing

		mnemonic function: test {name as thing}
			print('THING', repr(thing))				#THING 'stuff'
			print(dir())							#'D', 'cpt', 'hello', 'node', 'thing'
			print(cpt)								#{'thing': 'stuff'}

		setup:
			-node

		mnemonic function: test2 {name as thing}
			print(dir())							#'D', 'cpt', 'hello', 'thing'
			print(hello)							#world


	test stuff
	test2 stuff

''', normalize_block=True)




#Text tree dispatcher
from efforting.mvp6.processing.dispatcher import Regulations, Dispatcher, regex_rule, sub_dispatcher_rule
#from efforting.mvp6.processing.text_tree import Stack, Stack_Frame

from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Sequence, Structure
from efforting.mvp6 import symbol

import re

from efforting.mvp6.text.styling.terminal import stylize_and_render_document
from efforting.mvp6.text.styling import presets

from efforting.mvp6.context import context, python_code_execution_interface

#	print(stylize_and_render_document(dispatcher.node.value.body, style=presets.fruity))

mnemonic_title = View_Definition(
	string = Field_Conversion_Rule('tokens', string_formatter.process_item),
	tokens = Field_Conversion_Rule('string', tp.process_text),
)


class state_unpacker(Structure):
	state = M.positional()
	function = M.positional()

	def __call__(self, dispatcher):
		arguments = list()
		for key, value in self.state.items():
			match value:
				#TODO - improve this whole thing with naming and all
				case Contextual_Entry(context='msys', name='dispatcher'):
					arguments.append(dispatcher)

				case Contextual_Entry(context='cpt', name=name):
					arguments.append(dispatcher.state.match.value.match.groupdict()[name])

				case Contextual_Entry(context='ps', name='captures'):
					arguments.append(dispatcher.state.match.value.match.groupdict())

				case Contextual_Entry(context='ps', name=name):				#Dispatcher stack TODO rename
					arguments.append(getattr(dispatcher, name).value)

				case Contextual_Entry(context='ctx', name=name):
					arguments.append(dispatcher.state.context[name])

				case unhandled:
					raise Exception(value)

		return self.function(*arguments)


class Pending_Mnemonic_Processor(Structure):
	regulations = M.positional()
	mnemonic = M.positional()

	def __call__(self, function):
		self.regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item(self.mnemonic)), Text_Tree_Dispatcher_Action(function)))
		return function

class load_structure(Structure):
	target = M.positional()

	def __call__(self, dispatcher):
		return self.target(**dispatcher.state.match.value.match.groupdict())



class Mnemonic_Tree_Regulations(Regulations):
	def aggregate_matches(self, aggregator, item):
		found = False
		for rule in self.rules:
			match rule:	#TODO use ABc
				case regex_rule():
					match_item = item.string

				#TODO - handle mnemonic pattern

				case unhandled:
					raise Exception()

			if not aggregator.accepting_work:
				break

			if match := rule.match(match_item):
				aggregator.aggregate(Rule_Match(rule, match_item, match))
				found = True


		if not found and self.fallback_rule:
			aggregator.aggregate(Rule_Match(self.fallback_rule, item, symbol.miss))


	def register_mnemonic_processor(self, mnemonic):
		return Pending_Mnemonic_Processor(self, mnemonic)


	def register_mnemonic_structure(self, mnemonic, structure):
		self.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item(mnemonic)), Text_Tree_Dispatcher_Action(load_structure(structure))))




class Mnemonic_Tree_Dispatcher(Text_Tree_Dispatcher):
	#target_dispatcher = M.positional(factory=Stack)
	#execution_context = M.positional(factory=context)
	#context = M.positional(factory=Stack)

	# def on_behalf_of(self, dispatcher):
	# 	#NOTE - This feel a bit ugly, but it will have to do for now
	# 	state = dict(dispatcher.__getstate__())
	# 	state['name'] = self.name
	# 	state['regulations'] = self.regulations

	# 	return type(self)(**state)

	def on_behalf_of(self, dispatcher):
		#NOTE - This feel a bit ugly, but it will have to do for now
		state = dict(self.__getstate__())
		state['state'] = dispatcher.state
		return type(self)(**state)


	def process_item(self, title):
		if match := self.dispatch_item(title):
			#with Stack_Frame(self.title, title, self.match, match):
			with self.state._stack(title=title, match=match):
				return self.process_action(match.value)
		else:
			raise Exception(f'No match for {title!r}')	#TODO - default handler, better message

	def dispatch_node(self, node):
		title = mnemonic_title(string=node.title)

		if match := self.dispatch_item(title):
			#with Stack_Frame(self.node, node, self.title, title, self.match, match):
			with self.state._stack(node=node, title=title, match=match):
				return self.process_action(match.value)
		else:
			raise Exception(f'No match for {title!r} in {self.name!r}')	#TODO - default handler, better message





regex_regulations = Mnemonic_Tree_Regulations()
amend_regex_regulations = Mnemonic_Tree_Regulations()
amend_variable_regex_regulations = Mnemonic_Tree_Regulations()

class Exclude(Structure):
	name = M.positional()

class Contextual_Entry(Structure):
	context = M.positional()
	name = M.positional()

class Alias(Structure):
	value = M.positional()
	name = M.positional()

amend_variable_regex_regulations.register_mnemonic_structure('-{name}', Exclude)
amend_variable_regex_regulations.register_mnemonic_structure('{name as context}.{name}', Contextual_Entry)

@amend_variable_regex_regulations.register_mnemonic_processor('{pattern} as {name}')
def amend_current_processor_setup(dispatcher):
	pattern, name = dispatcher.state.match.value.match.groups()
	return Alias(dispatcher.process_item(mnemonic_title(string=pattern)), name)



@amend_regex_regulations.register_mnemonic_processor('setup[:]')
def amend_current_processor_setup(dispatcher):
	state_setup = dispatcher.state.context['state_setup']
	state_setup.extend(amend_variable_current_processor_dispatcher.on_behalf_of(dispatcher).dispatch_tree(dispatcher.state.node.body).value)

@amend_regex_regulations.register_mnemonic_processor('mnemonic function[:] {pattern}')
def amend_current_processor_mnemonic_function(dispatcher):
	state_setup = dispatcher.state.context['state_setup']

	state = dict(dispatcher=Contextual_Entry('ps', 'dispatcher'))

	def resolve_entry(entry):
		match entry:
			case Contextual_Entry():
				return entry.name, entry

			case Alias():
				sub_name, sub_value = resolve_entry(entry.value)
				return entry.name, sub_value

			case Exclude():
				return entry.name, symbol.exclude

			case unhandled:
				raise Exception(unhandled)

	for entry in state_setup:
		name, value = resolve_entry(entry)
		if value is symbol.exclude:
			state.pop(name)
		else:
			state[name] = value


	arguments = ', '.join(state.keys())

	pattern = dispatcher.state.match.value.match.groupdict()['pattern']

	target_dispatcher = dispatcher.state.target_dispatcher
	body = Text_Tree_Listing.from_title_and_body(f'def handler({arguments}):', dispatcher.state.node.body, clean_body=True)

	sc = dispatcher.state.execution_context.sub_context()
	python_code_execution_interface.exec_in_context(sc, body.to_str())
	action = Text_Tree_Dispatcher_Action(state_unpacker(state, sc.require('handler')))

	target_dispatcher.regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item(pattern)), action))



@regex_regulations.register_mnemonic_processor('amend current processor[:]')
def amend_current_processor(dispatcher):
	#with Stack_Frame(dispatcher.target_dispatcher, dispatcher, dispatcher.context, dict(state_setup=list())):
	with dispatcher.state._stack(target_dispatcher=dispatcher, context=dict(state_setup=list())):
		amend_current_processor_dispatcher.on_behalf_of(dispatcher).dispatch_tree(dispatcher.state.node.body)



bootstrap_dispatcher = Mnemonic_Tree_Dispatcher('bootstrap_dispatcher', regex_regulations)
amend_current_processor_dispatcher = Mnemonic_Tree_Dispatcher('amend_current_processor_dispatcher', amend_regex_regulations)
amend_variable_current_processor_dispatcher = Mnemonic_Tree_Dispatcher('amend_variable_current_processor_dispatcher', amend_variable_regex_regulations)

#with Stack_Frame(bootstrap_dispatcher.context, dict(hello='world')):
with bootstrap_dispatcher.state._stack(context=dict(hello='world'), execution_context=context()):
	bootstrap_dispatcher.dispatch_tree(test_tree)
