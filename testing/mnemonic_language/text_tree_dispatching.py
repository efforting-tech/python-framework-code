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

#print(mnemonic_to_regex.process_item('hello world[:] {name as thing}'))
#exit()

test_tree = create_text_tree_document_from_str('''

	amend current processor:
		setup:
			PS: node, captures as cpt
			CTX: hello
			MSYS: -processor_state, processor_state as PS
			CPT: thing

		mnemonic function: test {name as thing}
			#print('THING', thing)
			print(dir())	#'PS', 'cpt', 'hello', 'node', 'thing'
			#print(cpt)		#{'thing': 'stuff'}

		setup:
			PS: -node

		mnemonic function: test2 {name as thing}
			print(dir())	#'PS', 'cpt', 'hello', 'thing'


	test stuff
	test2 stuff

''', normalize_block=True)




# regulations = Regulations()

# def test_func(dispatcher):
# 	print(dispatcher)

# regulations.rules.append(generic_data_condition(mttp.process_item(tp.process_text('amend current processor[:]')), Text_Tree_Dispatcher_Action(test_func)))

# d = Text_Tree_Dispatcher(regulations, title_preprocessor=tp.process_text)





# print(d.dispatch_node(test_tree))
# exit()





#Text tree dispatcher
from efforting.mvp6.processing.dispatcher import Regulations, Dispatcher, regex_rule, sub_dispatcher_rule
from efforting.mvp6.processing.text_tree import Stack, Stack_Frame

from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Sequence, Structure
from efforting.mvp6 import symbol


#print(mttp.process_item(tp.process_text('amend current processor[:]')))




import re

from efforting.mvp6.text.styling.terminal import stylize_and_render_document
from efforting.mvp6.text.styling import presets

from efforting.mvp6.context import context, python_code_execution_interface

#	print(stylize_and_render_document(dispatcher.node.value.body, style=presets.fruity))

mnemonic_title = View_Definition(
	string = Field_Conversion_Rule('tokens', string_formatter.process_item),
	tokens = Field_Conversion_Rule('string', tp.process_text),
)


class Mnemonic_Tree_Regulations(Regulations):
	def aggregate_matches(self, aggregator, item):
		found = False
		for rule in self.rules:
			match rule:	#TODO use ABc
				case regex_rule():
					match_item = item.string

				#TODO - handle mnemonic pattern

				case undhandled:
					raise Exception()

			if not aggregator.accepting_work:
				break

			if match := rule.match(match_item):
				aggregator.aggregate(Rule_Match(rule, match_item, match))
				found = True


		if not found and self.fallback_rule:
			aggregator.aggregate(Rule_Match(self.fallback_rule, item, symbol.miss))

class Mnemonic_Tree_Dispatcher(Text_Tree_Dispatcher):
	target_dispatcher = M.positional(factory=Stack)
	execution_context = M.positional(factory=context)

	def on_behalf_of(self, dispatcher):
		#NOTE - This feel a bit ugly, but it will have to do for now
		state = dispatcher.__getstate__()
		state['name'] = self.name
		state['regulations'] = self.regulations
		return type(self)(**state)

	def dispatch_node(self, node):
		title = mnemonic_title(string=node.title)

		if match := self.dispatch_item(title):
			with Stack_Frame(self.node, node, self.title, title, self.match, match):
				return self.process_action(match.value)
		else:
			raise Exception(f'No match for {title!r}')	#TODO - default handler, better message


def amend_current_processor(dispatcher):
	print('AMEND', dispatcher)

	with Stack_Frame(dispatcher.target_dispatcher, dispatcher):
		print('In stack')
		amend_current_processor_dispatcher.on_behalf_of(dispatcher).dispatch_tree(dispatcher.node.value.body)

		  #).dispatch_tree(dispatcher.node.value.body)
		#amend_current_processor_dispatcher.dispatch_tree(dispatcher.node.value.body)
		print('Out stack')


	return 123


def amend_current_processor_setup(dispatcher):
	print('Setup!')
	return 'set'


def amend_current_processor_mnemonic_function(dispatcher):
	print('MNEMONIC!', dispatcher.match.value.value.match.groupdict()['pattern'])
	pattern = dispatcher.match.value.value.match.groupdict()['pattern']

	#body = dispatcher.node.value.body.editable_copy()
	#body.normalize_block()

	target_dispatcher = dispatcher.target_dispatcher.value
	body = Text_Tree_Listing.from_title_and_body(f'def handler(dispatcher):', dispatcher.node.value.body, clean_body=True)

	sc = dispatcher.execution_context.sub_context()
	python_code_execution_interface.exec_in_context(sc, body.to_str())
	action = Text_Tree_Dispatcher_Action(sc.require('handler'))


	target_dispatcher.regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item(pattern)), action))

	return 'mne'






regex_regulations = Mnemonic_Tree_Regulations()
regex_regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item('amend current processor[:]')), Text_Tree_Dispatcher_Action(amend_current_processor)))
bootstrap_dispatcher = Mnemonic_Tree_Dispatcher('bootstrap_dispatcher', regex_regulations)

amend_regex_regulations = Mnemonic_Tree_Regulations()
amend_regex_regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item('setup[:]')), Text_Tree_Dispatcher_Action(amend_current_processor_setup)))
amend_regex_regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item('mnemonic function[:] {pattern}')), Text_Tree_Dispatcher_Action(amend_current_processor_mnemonic_function)))
#amend_regex_regulations.rules.append(regex_rule(re.compile(mnemonic_to_regex.process_item('amend [:]')), Text_Tree_Dispatcher_Action(test_func)))
amend_current_processor_dispatcher = Mnemonic_Tree_Dispatcher('amend_current_processor_dispatcher', amend_regex_regulations)

# main_regulations = Regulations()
# main_regulations.rules.append(sub_dispatcher_rule(bootstrap_dispatcher))

# print(Mnemonic_Tree_Dispatcher(main_regulations).dispatch_node(test_tree))

print(bootstrap_dispatcher.dispatch_tree(test_tree))

#mlp.context.set('hello', 'world')
#mlp.process_tree(test_tree)

