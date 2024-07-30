from efforting.mvp6 import symbol
from efforting.mvp6.matching import data_condition as DC
from efforting.mvp6.mnemonic_language.parser import tp
from efforting.mvp6.mnemonic_language.parsing_rules import element_comparator
from efforting.mvp6.mnemonic_language.rudimentary_definition_helpers import join_sequence, word, optional, literal, ws
from efforting.mvp6.mnemonic_language.structures import Optional, Mnemonic, Expression
from efforting.mvp6.mnemonic_language.styling_rules import styling_processor

from efforting.mvp6.text.styling.terminal import render_styled_text
from efforting.mvp6.text.styling import presets as SP

T = symbol.text.token

v3 = join_sequence(ws,
	word('mnemonic'),
	[
		word('function'),
		optional(literal(':'))
	],
	DC.Capture_Remaining('pattern'),
require_sequence_type=Mnemonic)

test_tokens = tp.process_text('mnemonic function: define tree processor[:] {name}')

ec = element_comparator()
assert ec.compare_items(v3, test_tokens)


styled_text = styling_processor.process_item(test_tokens)
print(render_styled_text(styled_text, SP.fruity))

styled_text = styling_processor.process_item(ec.captures['pattern'])
print(render_styled_text(styled_text, SP.fruity))
