from efforting.mvp4 import type_system as RTS
from efforting.mvp4.type_system.bases import public_base

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

class append_message(public_base):
	name = RTS.positional()
