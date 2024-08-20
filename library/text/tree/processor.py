#TODO - is this used or deprecated?

from ...record.base.public import Structure
from ...record import member as M

from ...str.interface import String_Interface


from ... import symbol

T = symbol.text.token

def tokenize_mnemonic(mnemonic):
	yield from String_Interface.regex_tokenize(mnemonic, {
		T.left_curly_bracket: r'\{',
		T.word: r'\w+',
		T.whitespace: r'\s+',
		T.literal: None,
	})


def tokenize_mnemonic_expression(mnemonic):
	yield from String_Interface.regex_tokenize(mnemonic, {
		T.right_curly_bracket: r'\}',
		T.word: r'\w+',
		T.whitespace: r'\s+',
		T.literal: None,
	})

# class Rule_Set(Structure):
# 	rules = M.positional(factory=list)
# 	fallback = M.positional(None)




# 	def add_mnemonic_rule(self, mnemonic, action=None):

# 		for token in tokenize_mnemonic(mnemonic):
# 			if token.token is T.left_curly_bracket:
# 				print('Must enter sub tokenizer')


# 			print(token.token, token.match)




# class Processor(Structure):
# 	rules = M.positional(factory=Rule_Set)

# 	def process_node(self, node):
# 		print(node.title)


