#This is just some stuff to catch when doing coverage - it shall be removed
def test():
	for index, token in enumerate(outer_expression_tokenizer.tokenize('test {of some} thing')):
		match (index, token):
			case 0, token_match(classification=CL.word, match='test'):
				pass
			case 1, token_match(classification=CL.pattern_expression, match=(
				token_match(classification=CL.word, match='of'),
				token_match(classification=CL.word, match='some'))):
				pass
			case 2, token_match(classification=CL.word, match='thing'):
				pass
			case _:
				raise Exception(index, token)
