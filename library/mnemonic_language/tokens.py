from .. import symbol
T = symbol.text.token

#NOTE - would be nice to first just define our token patterns, maybe using some shorthand for when we build the sub parser.
#		alternatively we build the ruleset in an hierarchial manner
common = {
	T.word: r'\w+',
	T.whitespace: r'\s+',
	T.literal: None,
}

mnemonic_expression = {
	T.right_curly_bracket: r'\}',
	**common,
}

opt_expression = {
	T.right_square_bracket: r'\]',
	T.left_square_bracket: r'\[',
	**common,
}

mnemonic = {
	T.left_curly_bracket: r'\{',
	T.left_square_bracket: r'\[',
	**common,
}

