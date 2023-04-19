#Testing using the prompt-toolkit library
from application import command_parser

#Step one is that we tidy up from t2 to get better namespace separation and easier to do experiments




# print(command_parser.process_text('''

# 	set history backlog 5 + 7
# 	# `symbol.OK´

# 	history backlog
# 	# display_setting('history.backlog')

# 	insert system message before 1: This is another message
# 	# messages_added('message.system', 1)

# 	append system message: This is another message
# 	# messages_added('message.system', 1)

# 	insert system message after 1: Wee list manipulation
# 	# messages_added('message.system', 1)

# 	append multiline system message
# 		this is a multi line
# 		system message that we
# 		are inserting here
# 		but it is different if we do it
# 		in an interactive way
# 	# messages_added('message.system', 1)

# 	show system message 1
# 	# message_selection('message.system', (1,))

# 	delete system message 2
# 	# messages_deleted('message.system', 1)

# 	show system messages
# 	# message_selection('message.system', `symbol.ALL´)

# 	edit system message 1
# 		replaced with this stuff
# 	# messages_edited('message.system', 1)

# '''))