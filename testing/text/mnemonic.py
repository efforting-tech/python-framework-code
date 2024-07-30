from efforting.mvp6 import symbol, ABC
from efforting.mvp6.document import structures as DS
from efforting.mvp6.iteration import branchable_iterator, Switchable_Iterator
from efforting.mvp6.matching import data_condition as DC
from efforting.mvp6.mnemonic_language.parser import tp
from efforting.mvp6.mnemonic_language.rudimentary_definition_helpers import join_sequence, word, optional, literal, ws
from efforting.mvp6.mnemonic_language.structures import Optional, Mnemonic, Expression
from efforting.mvp6.processing import LUT_Processor, Type_LUT_Processor, Type_LUT_Comparator, Call_Comparator_Function
from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Structure, Sequence
from efforting.mvp6.str.interface import String_Interface
from efforting.mvp6.text.parsing import Token_Parser
from efforting.mvp6.text.parsing.structures import Token_Stream, Enter_Sub_Parser

T = symbol.text.token



test = 'title[:] {text}'
print(tp.process_text(test))
print()



v1 = DC.Sequence(word('define'), ws, optional(literal(':')), ws, DC.Capture_Remaining())

v2 = DC.Sequence(
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.word, match=DC.Structure_Match(match='define'))),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	(DC.Type_Instance(Optional) & DC.Sequence(
		(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.literal, match=DC.Structure_Match(match=':'))),
	)),
	(DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=T.whitespace)),
	DC.Capture_Remaining(),
)


print(v1 == v2)
print()


#v3 = join_sequence(ws, word('mnemonic'), [word('function'), optional(literal(':'))], DC.Capture_Remaining(), require_sequence_type=Mnemonic)

v3 = join_sequence(ws,
	word('mnemonic'),
	[
		word('function'),
		optional(literal(':'))
	],
	DC.Capture_Remaining('pattern'),
require_sequence_type=Mnemonic)


print(v3)

test_tokens = tp.process_text('mnemonic function: define tree processor[:] {name}')
print()
print(test_tokens)

print()
from efforting.mvp5.lazy_resources import acquire
import os
os.system('tabs 4')
dump = acquire('terminal_dump')


#TODO - custom data dumping!
#dump(v3, skip_underscore=True)

#for t in test_tokens:
#	print(t)



#When we compare this, we may want a rule system since we may want to do very different things in different circumstances

#Next up - compare test_tokens with v3 using a comparing processor

from efforting.mvp6.mnemonic_language.parsing_rules import element_comparator

ec = element_comparator()
print(ec.compare_items(v3, test_tokens))
for item in ec.captures['pattern']:
	print(item)

