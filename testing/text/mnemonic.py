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
print(ec.captures)



styled_text = styling_processor.process_item(test_tokens)
print(render_styled_text(styled_text, SP.fruity))

styled_text = styling_processor.process_item(ec.captures['pattern'])
print(render_styled_text(styled_text, SP.fruity))

from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.processing.text_tree import Mnemonic_Text_Tree_Processor

test_tree = create_text_tree_document_from_str('''

	mnemonic function: define tree processor[:] {name}

		print('We should define the processor')

''', normalize_block=True)

ttp = Mnemonic_Text_Tree_Processor('ttp')


def unpack_dict(target, *keys):
	yield from (target[k] for k in keys)


#@ttp.rules.register_mnemonic('mnemonic function[:] {pattern}')
@ttp.rules.register_mnemonic(v3)
def process_mnemonic(processor_state):
	[pattern] = unpack_dict(processor_state.captures, 'pattern')
	print(pattern)

	#Here we must process pattern and translate things.
	#For instance {pattern} should be turned to DC.Capture_Remaining('pattern') while {name} should be word() & DC.Capture('name'),




ttp().process_tree(test_tree)