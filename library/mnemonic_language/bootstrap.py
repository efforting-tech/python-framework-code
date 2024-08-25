#TODO - clean out unused imports
from .. import symbol
from ..context import context, python_code_execution_interface
from ..data_view import View_Definition, Field_Conversion_Rule
from ..document import create_text_tree_document_from_str
from ..mnemonic_language.mnemonic_tokens_to_pattern import mttp
from ..mnemonic_language.parser import tp
from ..mnemonic_language.processing import mnemonic_to_regex
from ..mnemonic_language.string_formatting_rules import string_formatter
from ..processing.dispatcher import Regulations, Dispatcher, regex_rule, sub_dispatcher_rule
from ..processing.dispatcher import Regulations, Dispatcher, regex_rule, sub_dispatcher_rule, generic_data_condition, Rule_Match
from ..processing.text_tree import Text_Tree_Dispatcher, Text_Tree_Dispatcher_Action
from ..record import member as M
from ..record.base.public import Sequence, Structure
from ..text.styling import presets
from ..text.styling.terminal import stylize_and_render_document
from ..text.tree import Text_Tree_Listing

from ..document import create_text_tree_document_from_path
from ..resources import get_resource_path

import re


#NEXT UP - We started with the pattern recognizer and tokens but then we hit a snag here which we can solve but want to put off to later. This means we now mix regex and token pattern matches which we currently solved by using a fallback
#			I would prefer if we used a single regulations object but we had different sub regulations depending on if we should work with the tokens or the strings. I think a reasonable approach here is to have a data view object
#			that can have multiple views and define conversations between views. It can then automatically resolve items.

#NEXT UP - we are back at the inconsistency in who should keep track of the context/processor state. Maybe we should make a processor and leave the regulations outside of it
#			NOTE - after considering it for a bit I think we should have an abstract processor state that supports shallow copy so we can easily copy the state. That way processor can keep regulations and name and only have state instead of a bunch of
#					loose members like we do now
#			TODO - see above note
#			ADDENDUM - we should probably use the context object and stack the contexts


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
					arguments.append(getattr(dispatcher.state, name))

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


class return_value(Structure):
	value = M.positional()

	def __call__(self, dispatcher):
		return self.value


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


	def register_mnemonic_value(self, mnemonic,  value):
		self.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item(mnemonic)), Text_Tree_Dispatcher_Action(return_value(value))))



class Mnemonic_Tree_Dispatcher(Text_Tree_Dispatcher):
	regulations = M.positional(factory=Mnemonic_Tree_Regulations)
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

amend_variable_regex_regulations.register_mnemonic_value('#{pattern}', symbol.empty)

amend_variable_regex_regulations.register_mnemonic_structure('-{name}', Exclude)
amend_variable_regex_regulations.register_mnemonic_structure('{name as context}.{name}', Contextual_Entry)

amend_variable_regex_regulations.register_mnemonic_value('new context', symbol.mnemonic_context.manipulation.new_context)
amend_variable_regex_regulations.register_mnemonic_value('clear context', symbol.mnemonic_context.manipulation.clear_context)
amend_variable_regex_regulations.register_mnemonic_value('all captures', symbol.mnemonic_context.manipulation.all_captures)

@amend_variable_regex_regulations.register_mnemonic_processor('{pattern} as {name}')
def amend_current_processor_setup(dispatcher):
	pattern, name = dispatcher.state.match.value.match.groups()
	return Alias(dispatcher.process_item(mnemonic_title(string=pattern)), name)



@amend_regex_regulations.register_mnemonic_processor('setup[:]')
def amend_current_processor_setup(dispatcher):
	state_setup = dispatcher.state.context['state_setup']
	state_setup.extend(amend_variable_current_processor_dispatcher.on_behalf_of(dispatcher).dispatch_tree(dispatcher.state.node.body).value)


def prepare_state(dispatcher, captures):
	state_setup = dispatcher.state.context['state_setup']
	state = dict(dispatcher=Contextual_Entry('msys', 'dispatcher'))

	def resolve_entry(entry):
		match entry:
			case Contextual_Entry():
				return entry.name, entry

			case Alias():
				sub_name, sub_value = resolve_entry(entry.value)
				return entry.name, sub_value

			case Exclude():
				return entry.name, symbol.exclude

			case sym if sym in symbol.mnemonic_context.manipulation or sym is symbol.empty:	#TODO just let all symbols through? ABC.symbol?
				return None, sym

			case unhandled:
				raise Exception(unhandled)

	for entry in state_setup:
		name, value = resolve_entry(entry)
		if value is symbol.exclude:
			state.pop(name)
		elif value is symbol.mnemonic_context.manipulation.clear_context:
			state.clear()
		elif value is symbol.mnemonic_context.manipulation.new_context:
			state.clear()
			state.update(dispatcher=Contextual_Entry('msys', 'dispatcher'))	#TODO - a function to create new context (single source of truth)
		elif value is symbol.mnemonic_context.manipulation.all_captures:
			for name in captures:
				state[name] = Contextual_Entry('cpt', name)

		elif value is symbol.empty:
			pass
		else:
			state[name] = value

	return state


def create_mnemonic_handler(dispatcher, state):
	pattern = dispatcher.state.match.value.match.groupdict()['pattern']
	re_pattern = re.compile(mnemonic_to_regex.process_item(pattern))
	state = prepare_state(dispatcher, re_pattern.groupindex.keys())

	arguments = ', '.join(state.keys())

	target_dispatcher = dispatcher.state.target_dispatcher
	body = Text_Tree_Listing.from_title_and_body(f'def handler({arguments}):', dispatcher.state.node.body, clean_body=True)

	sc = dispatcher.state.execution_context.sub_context()
	python_code_execution_interface.exec_in_context(sc, body.to_str())
	#action = Text_Tree_Dispatcher_Action(state_unpacker(state, sc.require('handler')))

	target_dispatcher.regulations.rules.append(regex_rule(re_pattern, action))


def create_state_and_pattern(dispatcher):
	pattern = dispatcher.state.match.value.match.groupdict()['pattern']
	re_pattern = re.compile(mnemonic_to_regex.process_item(pattern))
	state = prepare_state(dispatcher, re_pattern.groupindex.keys())
	return state, re_pattern


def create_function(dispatcher, function_name, arguments):
	body = Text_Tree_Listing.from_title_and_body(f'def {function_name}({arguments}):', dispatcher.state.node.body, clean_body=True)
	sc = dispatcher.state.execution_context.sub_context()
	python_code_execution_interface.exec_in_context(sc, body.to_str())
	return sc.require(function_name)

@amend_regex_regulations.register_mnemonic_processor('mnemonic function[:] {pattern}')
def amend_current_processor_mnemonic_function(dispatcher):
	state, re_pattern = create_state_and_pattern(dispatcher)
	action = Text_Tree_Dispatcher_Action(state_unpacker(state, create_function(dispatcher, 'handler', ', '.join(state.keys()))))
	dispatcher.state.target_dispatcher.regulations.rules.append(regex_rule(re_pattern, action))

@amend_regex_regulations.register_mnemonic_processor('mnemonic value[:] {pattern}')
def amend_current_processor_mnemonic_value(dispatcher):
	state, re_pattern = create_state_and_pattern(dispatcher)
	value = state_unpacker(state, create_function(dispatcher, 'handler', ', '.join(state.keys())))(dispatcher)
	action = Text_Tree_Dispatcher_Action(return_value(value))
	dispatcher.state.target_dispatcher.regulations.rules.append(regex_rule(re_pattern, action))



@regex_regulations.register_mnemonic_processor('amend current processor[:]')
def amend_current_processor(dispatcher):
	#with Stack_Frame(dispatcher.target_dispatcher, dispatcher, dispatcher.context, dict(state_setup=list())):
	with dispatcher.state._stack(target_dispatcher=dispatcher, context=dict(state_setup=list())):
		amend_current_processor_dispatcher.on_behalf_of(dispatcher).dispatch_tree(dispatcher.state.node.body)



bootstrap_dispatcher = Mnemonic_Tree_Dispatcher('bootstrap_dispatcher', regex_regulations)
amend_current_processor_dispatcher = Mnemonic_Tree_Dispatcher('amend_current_processor_dispatcher', amend_regex_regulations)
amend_variable_current_processor_dispatcher = Mnemonic_Tree_Dispatcher('amend_variable_current_processor_dispatcher', amend_variable_regex_regulations)

#with Stack_Frame(bootstrap_dispatcher.context, dict(hello='world')):
boot_tree = create_text_tree_document_from_path(get_resource_path('mnemonic_language_bootstrap.tdef'))

bootstrap_dispatcher.state._update(
	context=dict(
		#hello='world',
		#Mnemonic_Tree_Dispatcher=Mnemonic_Tree_Dispatcher,
		#amend_current_processor_dispatcher=amend_current_processor_dispatcher
	),
	execution_context=context(None, dict(
		__package__ = __package__,
		__name__ = __name__,

		Mnemonic_Tree_Dispatcher=Mnemonic_Tree_Dispatcher,
		amend_current_processor_dispatcher=amend_current_processor_dispatcher

	)),
)



bootstrap_dispatcher.dispatch_tree(boot_tree)



if False:

	#NEXT UP - we should harmonize the processing system and make it possible to setup chains/graphs for processing - there is WAY too much overlap as of now



	from .processing import Mnemonic_Text_Tree_Processor
	from ..document import create_text_tree_document_from_path
	from ..resources import get_resource_path
	from ..context import context
	#from ..processing.generic import Type_LUT_Processor, Identity_LUT_Processor, Regex_Processor
	from .parser import tp
	from .string_formatting_rules import string_formatter
	from .structures import Mnemonic, Optional, Expression
	from ..document import structures as DS
	from .. import symbol
	T = symbol.text.token

	import re
	#print(re.compile(r'amend\s+current\s+processor\s*(?::)?').fullmatch('amend current processor'))

	#mnemonic_to_regex = Regex_Processor('mnemonic_to_regex')

	#mnemonic_to_regex.process_item('amend current processor[:]')





	root_context = context('root', dict(
		#...
	))


	mnemonic_language_processor = Mnemonic_Text_Tree_Processor('mnemonic_language_processor')
	amend_definition_processor = Mnemonic_Text_Tree_Processor('amend_definition_processor')

	from .structures import Mnemonic, pending_function_with_advanced_unwrapper, pending_mnemonic_implementation, context_manipulation


	@amend_definition_processor.register_mnemonic('setup[:]')
	def setup_processor_handler(processor_state):
		pass


	@amend_definition_processor.register_mnemonic('mnemonic function[:] {pattern}')
	def mnemonic_function(processor_state):
		[pattern] = processor_state.match.groups()
		target_processor = processor_state.context.require('target_processor')
		pending_mnemonic_implementation = processor_state.context.require('pending_mnemonic_implementation').copy() #We copy so we get current state
		register_mnemonic_function(target_processor, pattern, pending_function_with_advanced_unwrapper(processor_state.node.body, pending_mnemonic_implementation))


	@mnemonic_language_processor.register_mnemonic('amend current processor[:]')
	def should_amend(processor_state):
		#TODO we should improve api so we can make a new state while doing adjustments
		ps = processor_state.with_processor(amend_definition_processor)

		ps.context = ps.context.sub_context(dict(
			target_processor=processor_state,
			pending_mnemonic_implementation = pending_mnemonic_implementation(),
		))
		ps.process_tree(processor_state.node.body)





	mlp = mnemonic_language_processor(state=dict(context=root_context))
	boot_tree = create_text_tree_document_from_path(get_resource_path('mnemonic_language_bootstrap.tdef'))
	mlp.process_tree(boot_tree)