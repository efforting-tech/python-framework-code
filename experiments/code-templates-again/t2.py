from efforting.mvp4.text_processing.improved_text_node_processor import A
from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.bases import public_base
from efforting.mvp4.rudimentary_features.code_manipulation.templating.pp_context import context
from efforting.mvp4.rudimentary_features.code_manipulation.templating.source_tracker import source_tracker
# from efforting.mvp4.text_processing.improved_tokenization import regex_parser
from efforting.mvp4.text_processing.re_match_processing import match_iterator
from efforting.mvp4.development_utils import use_linecache_traceback
from efforting.mvp4.text_nodes import text_node
from efforting.mvp4.text_processing.mnemonic_tree_processor import mnemonic_tree_processor
from efforting.mvp4.symbols import register_symbol
ALL = register_symbol('ALL')
NOP = register_symbol('NOP')
OK = register_symbol('OK')

#TODO: look into using https://python-prompt-toolkit.readthedocs.io/en/master/pages/asking_for_input.html#nested-completion



use_linecache_traceback()
local_context = context(tracker = source_tracker())

rule_parser = mnemonic_tree_processor(context=local_context)
rule_parser.context.locals.update(P=rule_parser, C=rule_parser.context)


settings = dict()

#TODO - use namespaces for responses, actions and so forth since we are starting to have colissions
#TODO - use some base class for responses

class messages_mutated(public_base):
	name = RTS.positional()
	count = RTS.positional()

class messages_deleted(messages_mutated):
	pass

class messages_edited(messages_mutated):
	pass

class messages_added(messages_mutated):
	pass

class message_selection(public_base):
	name = RTS.positional()
	message_indices = RTS.positional()

class display_setting(public_base):
	setting = RTS.positional()

class edit_message(public_base):
	name = RTS.positional()
	index = RTS.positional()

#todo - base class for actions

class no_command:
	@staticmethod
	def take_action(processor, node, match):
		return NOP


class set_setting(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		value = rule_parser.context.eval_expression_temporary_tracker(match.group('value'))
		settings[self.name] = value
		return OK

class show_setting(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		return display_setting(self.name)

class show_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		n = match.groupdict()

		if selection := n.pop('selection', None):
			indices = (int(selection),)	#TODO - support ranges and multiple indices
		else:
			indices = ALL
		return message_selection(self.name, indices)


class delete_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('selection'))	#TODO - support ranges and multiple indices

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		settings[self.name].pop(index)

		return messages_deleted(self.name, 1)

class insert_message_before(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))
		message = match.group('message')

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		settings[self.name].insert(index, message)

		return messages_added(self.name, 1)

class insert_message_after(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))
		message = match.group('message')

		#The index will be base 1 and needs to be converted into base 0, but since we are inserting AFTER index, we don't need to change the positive index
		if index == -1:	#This is a special case where we are appending the message at the end
			settings[self.name].append(message)
			return
		elif index < -1:
			index += 1

		settings[self.name].insert(index, message)

		return messages_added(self.name, 1)

class append_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		message = match.group('message')
		settings[self.name].append(message)

		return messages_added(self.name, 1)


class append_multiline_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		if node.body.has_contents:	#Not interactive
			settings[self.name].append(node.body)
			return messages_added(self.name, 1)
		else:
			#This should be implemented by using some sort of return value that indicates it is a multiline thing with a callback
			return write_message(self.name)


class edit_multiline_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		if node.body.has_contents:	#Not interactive
			settings[self.name] = node.body
			return messages_edited(self.name, 1)
		else:
			#This should be implemented by using some sort of return value that indicates it is a multiline thing with a callback
			return edit_message(self.name, index)




class PENDING(public_base):
	positional = RTS.all_positional()
	named = RTS.all_named()

	def take_action(self, processor, node, match):
		raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature


def add_setting(name, syntax, default=None):
	rule_parser.add_mnemonic_action(f'set {syntax} {{value...}}', set_setting(name))
	rule_parser.add_mnemonic_action(f'{syntax}', show_setting(name))
	settings[name] = default

def add_message_queue(name, singular_syntax, plural_syntax, default=None):
	#rule_parser.add_mnemonic_action(f'set {syntax} {{value...}}', set_setting(name))
	rule_parser.add_mnemonic_action(f'show {plural_syntax}', show_message(name))	#TODO - in the future we want to be able to do:  '(show|list|view) {syntax}'

	#Here index is implied to be a single message while selection could be a range or several indices
	rule_parser.add_mnemonic_action(f'show {singular_syntax} {{selection...}}', show_message(name))
	rule_parser.add_mnemonic_action(f'delete {singular_syntax} {{selection...}}', delete_message(name))
	rule_parser.add_mnemonic_action(f'edit {singular_syntax} {{index...}}', edit_multiline_message(name))

	rule_parser.add_mnemonic_action(f'insert {singular_syntax} before {{index...}}: {{message...}}', insert_message_before(name))
	rule_parser.add_mnemonic_action(f'insert {singular_syntax} after {{index...}}: {{message...}}', insert_message_after(name))
	rule_parser.add_mnemonic_action(f'append {singular_syntax}: {{message...}}', append_message(name))
	rule_parser.add_mnemonic_action(f'append multiline {singular_syntax}', append_multiline_message(name))

	settings[name] = default

add_setting('history.backlog', 'history backlog', 4)
add_message_queue('message.system', 'system message', 'system messages', ['You are a helpful, cheerful and generally excited creative assistant'])

#add_setting('message.system', 'system messages', ['You are a helpful, cheerful and generally excited creative assistant'])

#@rule_parser.mnemonic_rule('')

rule_parser.add_mnemonic_action('#{anything...}', no_command)

print(rule_parser.process_text('''

	set history backlog 5 + 7
	# `symbol.OK´

	history backlog
	# display_setting('history.backlog')

	insert system message before 1: This is another message
	# messages_added('message.system', 1)

	append system message: This is another message
	# messages_added('message.system', 1)

	insert system message after 1: Wee list manipulation
	# messages_added('message.system', 1)

	append multiline system message
		this is a multi line
		system message that we
		are inserting here
		but it is different if we do it
		in an interactive way
	# messages_added('message.system', 1)

	show system message 1
	# message_selection('message.system', (1,))

	delete system message 2
	# messages_deleted('message.system', 1)

	show system messages
	# message_selection('message.system', `symbol.ALL´)

	edit system message 1
		replaced with this stuff
	# messages_edited('message.system', 1)

'''))

# @rule_parser.optional_text_mnemonic('NOTE')
# def note():
# 	1/0

# @rule_parser.mnemonic_rule('MODE OF {mode_type...}: {name...}')
# def mode_of_something():
# 	global stuff
# 	stuff = 123

# 	C.set('stuff', 456)

# 	print('MODE', mode_type, name)



# import linecache
# print(linecache.cache.keys())


# rule_parser.process_text('''

# 	NOTE: thing
# 		stuff

# 	MODE OF STUFF: the stuff mode

# ''')

