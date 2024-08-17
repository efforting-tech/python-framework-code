#NEXT UP - we should harmonize the processing system and make it possible to setup chains/graphs for processing - there is WAY too much overlap as of now


from .processing import Mnemonic_Text_Tree_Processor
from ..document import create_text_tree_document_from_path
from ..resources import get_resource_path
from ..context import context
#from ..processing.generic import Type_LUT_Processor, Identity_LUT_Processor, Regex_Processor
from .parser import tp
from .string_formatting_rules import string_formatter
from .structures import Mnemonic, Optional, Expression
from ..document import structures as DS
from .. import symbol
T = symbol.text.token

import re
#print(re.compile(r'amend\s+current\s+processor\s*(?::)?').fullmatch('amend current processor'))

#mnemonic_to_regex = Regex_Processor('mnemonic_to_regex')

#mnemonic_to_regex.process_item('amend current processor[:]')





root_context = context('root', dict(
	#...
))


mnemonic_language_processor = Mnemonic_Text_Tree_Processor('mnemonic_language_processor')
amend_definition_processor = Mnemonic_Text_Tree_Processor('amend_definition_processor')

from .structures import Mnemonic, pending_function_with_advanced_unwrapper, pending_mnemonic_implementation, context_manipulation


@amend_definition_processor.register_mnemonic('setup[:]')
def setup_processor_handler(processor_state):
	pass


@amend_definition_processor.register_mnemonic('mnemonic function[:] {pattern}')
def mnemonic_function(processor_state):
	[pattern] = processor_state.match.groups()
	target_processor = processor_state.context.require('target_processor')
	pending_mnemonic_implementation = processor_state.context.require('pending_mnemonic_implementation').copy() #We copy so we get current state
	register_mnemonic_function(target_processor, pattern, pending_function_with_advanced_unwrapper(processor_state.node.body, pending_mnemonic_implementation))


@mnemonic_language_processor.register_mnemonic('amend current processor[:]')
def should_amend(processor_state):
	#TODO we should improve api so we can make a new state while doing adjustments
	ps = processor_state.with_processor(amend_definition_processor)

	ps.context = ps.context.sub_context(dict(
		target_processor=processor_state,
		pending_mnemonic_implementation = pending_mnemonic_implementation(),
	))
	ps.process_tree(processor_state.node.body)





mlp = mnemonic_language_processor(state=dict(context=root_context))
boot_tree = create_text_tree_document_from_path(get_resource_path('mnemonic_language_bootstrap.tdef'))
mlp.process_tree(boot_tree)