from ....improved_tokenizer import improved_tokenizer
from ....improved_mnemonic_tree_processor import actions as A
from ....improved_mnemonic_tree_processor import conditions as C

from .ast import placeholder

#Tokenizer should only be used when defining templates since otherwise we may evaluate multiple times which can cause issues
template_tokenizer = improved_tokenizer(name='template_tokenizer')
template_tokenizer.add_rule(C.matches_regex(r'\\«'), A.return_value('«'))
template_tokenizer.add_rule(C.matches_regex(r'\\»'), A.return_value('»'))
template_tokenizer.add_rule(C.matches_regex(r'«(.*?)»'), A.return_processed_match(placeholder.from_match))
template_tokenizer.default_action = A.return_processed_match(lambda match: match.group())
