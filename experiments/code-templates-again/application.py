from efforting.mvp4.development_utils import use_linecache_traceback
from efforting.mvp4.rudimentary_features.code_manipulation.templating.pp_context import context
from efforting.mvp4.rudimentary_features.code_manipulation.templating.source_tracker import source_tracker
from efforting.mvp4.text_processing.mnemonic_tree_processor import mnemonic_tree_processor, command_pattern_processor

from traceback import print_exception


import pending_command as PC
import command_status as CS
import re

from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.rts_types import MISS	#TODO from better location

from efforting.mvp4.type_system.bases import public_base
from efforting.mvp4 import pattern_matching as PM

from efforting.mvp4.text_processing.re_tokenization import SKIP
from efforting.mvp4.text_processing import command_pattern_types as CPT


from prompt_toolkit.completion import NestedCompleter
from constants import OK, NO_SUCH_COMMAND, NOT_IMPLEMENTED, ALL, SHOW_SETTINGS

use_linecache_traceback()
settings = dict()
local_context = context(tracker = source_tracker(), locals=dict(
	settings=settings,
	completer=NestedCompleter({}),
))




from efforting.mvp4.generic_processing.generic_processing import generic_processor

class priority_dict_lookup_by_attribute(public_base):
	attribute = RTS.positional()
	source_list = RTS.all_positional()

	def process_item(self, item):
		name = getattr(item, self.attribute)
		for source in self.source_list:
			if (result := source.get(name, MISS)) is not MISS:
				return result

		raise Exception(item)

class priority_dict_lookup_by_dunder_name(priority_dict_lookup_by_attribute):
	attribute = RTS.setting('__name__')



class lookup_item_process_result(public_base):
	lookup_function = RTS.positional()
	return_processor = RTS.positional()

	def process_item(self, item):
		return self.return_processor(self.lookup_function(item))

class processor_chain(public_base):
	sub_processors = RTS.all_positional()

	def process_item(self, item):
		for sp in self.sub_processors:
			item = sp(item)

		return item

#This processor looks up the name of something in the CPT module and then turns it into a type identity that can be used as a condition in a ruleset
command_pattern_to_type_identity_condition = lookup_item_process_result(
	priority_dict_lookup_by_dunder_name(CPT.__dict__).process_item,
	PM.type_identity,
).process_item




@generic_processor.from_class_and_settings(condition_parser=command_pattern_to_type_identity_condition)
class command_pattern_to_completer:

	#TODO - add support for file name completion?

	def sequential_pattern(self, item):
		sentence = (*(i for i in self.process_sequence_iteratively(item.sequence) if i is not SKIP), None)	#Also add explicit sentinel here to make logic in loop simpler

		chain = None
		pending = None
		for word in sentence:
			if pending is None:
				pending = chain = NestedCompleter(dict())
			else:
				if previous is None:	#Break on first catch all
					break

				pending.options[previous] = pending = NestedCompleter(dict())

			previous = word


		return chain

	def literal_text(self, item):
		return item.text

	def optional(self, item):	#TODO - we currently terminate here - we should rewrite the command pattern to completer to be able to support optional branches
		return

	def remaining_text(self, item):
		return

	def required_space(self, item):
		return SKIP


def merge_completers(target, source):
	#TODO - check if there is built in featuer for this in prompt toolkit

	for word, sub_completer in source.options.items():
		if existing := target.options.get(word):
			merge_completers(existing, sub_completer)
		else:
			target.options[word] = sub_completer	#Branch complete

class mnemonic_tree_processor_with_word_completion(mnemonic_tree_processor):
	def add_mnemonic_action_wc(self, mnemonic, action):

		pattern = command_pattern_processor.command_pattern_processor.process_text(mnemonic)
		inner = pattern.to_pattern()
		re_pattern = re.compile(rf'^{inner}$', re.I)

		merge_completers(self.context.accessor.completer, command_pattern_to_completer.process_item(pattern))
		self.rules.append((re_pattern, action))





command_parser = mnemonic_tree_processor_with_word_completion(context=local_context, default_action=PC.return_value(NO_SUCH_COMMAND))
command_parser.context.locals.update(P=command_parser, C=command_parser.context)


def add_setting(name, syntax, default=None):
	command_parser.add_mnemonic_action_wc(f'set {syntax} {{value...}}', PC.set_setting(name))
	command_parser.add_mnemonic_action_wc(f'get {syntax}', PC.show_setting(name))
	settings[name] = default

def add_message_queue(name, singular_syntax, plural_syntax, default=None):
	#command_parser.add_mnemonic_action(f'set {syntax} {{value...}}', set_setting(name))
	command_parser.add_mnemonic_action_wc(f'show {plural_syntax}', PC.show_message(name))	#TODO - in the future we want to be able to do:  '(show|list|view) {syntax}'

	#NOTE - multiline input is generally selected by omitting the trailing colon that allows for inline specification

	#Here index is implied to be a single message while selection could be a range or several indices
	command_parser.add_mnemonic_action_wc(f'show {singular_syntax} {{selection...}}', PC.show_message(name))
	command_parser.add_mnemonic_action_wc(f'delete {singular_syntax} {{selection...}}', PC.delete_message(name))
	command_parser.add_mnemonic_action_wc(f'edit {singular_syntax} {{index...}}', PC.edit_multiline_message(name))

	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} before {{index...}}: {{message...}}', PC.insert_message_before(name))
	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} after {{index...}}: {{message...}}', PC.insert_message_after(name))
	command_parser.add_mnemonic_action_wc(f'append {singular_syntax}: {{message...}}', PC.append_message(name))

	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} from file before {{index...}}: {{filename...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO
	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} from file after {{index...}}: {{filename...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO
	command_parser.add_mnemonic_action_wc(f'append {singular_syntax} from file {{filename...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO

	command_parser.add_mnemonic_action_wc(f'append {singular_syntax}', PC.append_multiline_message(name))

	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} before {{index...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO
	command_parser.add_mnemonic_action_wc(f'insert {singular_syntax} after {{index...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO
	command_parser.add_mnemonic_action_wc(f'move {singular_syntax} from {{from_index...}} to {{to_index...}}', PC.return_value(NOT_IMPLEMENTED))	#TODO

	command_parser.add_mnemonic_action_wc(f'clear {plural_syntax}', PC.return_value(NOT_IMPLEMENTED))	#TODO

	settings[name] = default

add_setting('history.backlog', 'history backlog', 4)
add_message_queue('message.system', 'system message', 'system messages', ['You are a helpful, cheerful and generally excited creative assistant'])
add_message_queue('message.pending', 'pending message', 'pending', [])
add_message_queue('message.history', 'historic message', 'history', [])


command_parser.add_mnemonic_action_wc('help', PC.return_value(NOT_IMPLEMENTED))
command_parser.add_mnemonic_action_wc('show settings', PC.return_value(SHOW_SETTINGS))
command_parser.add_mnemonic_action_wc('ask[:] {query...}', PC.return_value(NOT_IMPLEMENTED))
command_parser.add_mnemonic_action_wc('execute query', PC.return_value(NOT_IMPLEMENTED))



#Call super since this should not be part of auto completion
command_parser.add_mnemonic_action('#{anything...}', PC.no_command)


from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.input import ansi_escape_sequences



# Define custom key bindings
kb = KeyBindings()

from enum import Enum
class Additional_Keys(str, Enum):
	ControlEnter = 'c-enter'

Additional_Keys.ControlEnter.__objclass__ = Additional_Keys.ControlEnter.__class__ = Keys
Keys._value2member_map_[Additional_Keys.ControlEnter._value_] = Keys._member_map_[Additional_Keys.ControlEnter._name_] = Additional_Keys.ControlEnter

ansi_escape_sequences.ANSI_SEQUENCES["\x1b[27;5;13~"] = Keys.ControlEnter
#This requires you to bind the terminal emulator, in konsole for instance, bind Ctrl+Enter to \E[27;5;13~
#Unfortunately ctrl+enter is not well defined

ansi_escape_sequences.REVERSE_ANSI_SEQUENCES = ansi_escape_sequences._get_reverse_ansi_sequences()

@kb.add(Keys.ControlEnter)
def e_ctrl_enter(event):
	event.current_buffer.validate_and_handle()



#Testing evaluation loop

execute_pending_command = generic_processor(context=local_context)
class _execute_pending_command_implementation:
	#TODO - use human name (plural/singular) for reporting on messages and such

	@execute_pending_command.on_type_identity(CS.display_setting)
	def display_setting(self, item):
		value = self.context.accessor.settings[item.setting]
		print(f'    {value!r}')
		print()

	@execute_pending_command.on_type_identity(CS.messages_edited)
	def messages_edited(self, item):
		print(f'    Changed {item.count} entries in {item.name}')
		print()

	@execute_pending_command.on_type_identity(CS.messages_deleted)
	def messages_deleted(self, item):
		print(f'    Deleted {item.count} entries in {item.name}')
		print()

	@execute_pending_command.on_type_identity(CS.messages_added)
	def messages_added(self, item):
		print(f'    Added {item.count} entries in {item.name}')
		print()

	@execute_pending_command.on_type_identity(CS.edit_message)
	def edit_message(self, item):
		messages = self.context.accessor.settings[item.name]
		print(f'    Editing entry {item.index} in {item.name}')
		print()
		#We don't use history when editing a message, that gets messy
		updated = prompt('', default=messages[item.index-1], multiline=True, key_bindings=kb)
		print()
		#TODO - maybe have a predefined prompt so we don't have to pass in key_bindings?
		#TODO - convert index

		messages[item.index-1] = updated
		self.process_item(CS.messages_edited(item.name, 1))


	@execute_pending_command.on_type_identity(CS.append_message)
	def append_message(self, item):
		messages = self.context.accessor.settings[item.name]
		print(f'    Adding entry to {item.name}')
		print()
		#We don't use history when editing a message, that gets messy
		updated = prompt('', multiline=True, key_bindings=kb)
		print()
		#TODO - maybe have a predefined prompt so we don't have to pass in key_bindings?
		#TODO - convert index

		messages.append(updated)
		self.process_item(CS.messages_added(item.name, 1))



	@execute_pending_command.on_type_identity(CS.message_selection)
	def message_selection(self, item):
		messages = self.context.accessor.settings[item.name]
		if item.message_indices is ALL:
			heading = f'All entries in {item.name}\n'
			items_to_print = tuple(enumerate(messages, 1))
		else:
			heading = f'Selected entries in {item.name}\n'
			items_to_print = tuple((i, messages[i-1]) for i in item.message_indices)	#These indices are base 1 (we should convert it properly so negative works, we should call function for this)

		if len(items_to_print) == 0:
			if item.message_indices is ALL:
				heading = f'There are no entries in {item.name}'
			else:
				heading = f'The selection of {item.name} is empty'

		print(f'    {heading}')

		for index, value in items_to_print:
			print(f'    {index}\t{value!r}')	#TODO - call some nice formatter instead of printing like this

		print()


	@execute_pending_command.on_identity(OK)
	def command_ok(self, item):
		print('    OK')
		print()

	@execute_pending_command.on_identity(NO_SUCH_COMMAND)
	def no_such_command(self, item):
		print('    Unknown command. You can list available commands with "help".')
		print()

	@execute_pending_command.on_identity(NOT_IMPLEMENTED)
	def command_not_implemented(self, item):
		print('    Command is not yet implemented. Yell at developer.')
		print()

	@execute_pending_command.on_identity(SHOW_SETTINGS)
	def show_settings(self, item):
		print('    Settings')
		print()
		for key, value in sorted(self.context.accessor.settings.items()):
			print(f'    {key}\t{value!r}')	#TODO - use a formatter

		print()


from prompt_toolkit import PromptSession
session = local_context.accessor.session = PromptSession()



while True:

	q = session.prompt('Query: ', multiline=False, key_bindings=kb, completer=local_context.accessor.completer)
	try:
		action = command_parser.process_text_item(q)
		execute_pending_command.process_item(action)
	except Exception as e:
		print_exception(e)
		print()


