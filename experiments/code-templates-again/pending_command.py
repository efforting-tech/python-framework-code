from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.bases import public_base

from constants import ALL, NOP, OK
import command_status as CS

class no_command:
	@staticmethod
	def take_action(processor, node, match):
		return NOP


class set_setting(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		value = processor.context.eval_expression_temporary_tracker(match.group('value'))
		processor.context.accessor.settings[self.name] = value
		return OK

class show_setting(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		return CS.display_setting(self.name)

class show_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		n = match.groupdict()

		if selection := n.pop('selection', None):
			indices = (int(selection),)	#TODO - support ranges and multiple indices
		else:
			indices = ALL
		return CS.message_selection(self.name, indices)


class delete_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('selection'))	#TODO - support ranges and multiple indices

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		processor.context.accessor.settings[self.name].pop(index)

		return CS.messages_deleted(self.name, 1)

class insert_message_before(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))
		message = match.group('message')

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		processor.context.accessor.settings[self.name].insert(index, message)

		return CS.messages_added(self.name, 1)

class insert_message_after(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))
		message = match.group('message')

		#The index will be base 1 and needs to be converted into base 0, but since we are inserting AFTER index, we don't need to change the positive index
		if index == -1:	#This is a special case where we are appending the message at the end
			processor.context.accessor.settings[self.name].append(message)
			return CS.messages_added(self.name, 1)
		elif index < -1:
			index += 1

		processor.context.accessor.settings[self.name].insert(index, message)

		return CS.messages_added(self.name, 1)

class append_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		message = match.group('message')
		processor.context.accessor.settings[self.name].append(message)

		return CS.messages_added(self.name, 1)


class append_multiline_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		if node.body.has_contents:	#Not interactive
			processor.context.accessor.settings[self.name].append(node.body)
			return CS.messages_added(self.name, 1)
		else:
			#This should be implemented by using some sort of return value that indicates it is a multiline thing with a callback
			return CS.append_message(self.name)


class edit_multiline_message(public_base):
	name = RTS.positional()

	def take_action(self, processor, node, match):
		index = int(match.group('index'))

		if index > 0: #Adjustment is only done on positive values since negative are from the end
			index -= 1	#Adjust to base 0

		if node.body.has_contents:	#Not interactive
			processor.context.accessor.settings[self.name] = node.body
			return CS.messages_edited(self.name, 1)
		else:
			#This should be implemented by using some sort of return value that indicates it is a multiline thing with a callback
			return CS.edit_message(self.name, index)




class return_value(public_base):
	value = RTS.positional()

	def take_action(self, processor, node, match):
		return self.value




