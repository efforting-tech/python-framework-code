from ..context import context
from ..processing.text_tree import Mnemonic_Text_Tree_Processor
from .utilities import register_mnemonic_function, get_mnemonic, tokenize_text
from ..matching import data_condition as DC
from .. import symbol

mnemonic_language_processor = Mnemonic_Text_Tree_Processor('mnemonic_language_processor')
amend_definition_processor = Mnemonic_Text_Tree_Processor('amend_definition_processor')
processor_setup_processor = Mnemonic_Text_Tree_Processor('processor_setup_processor')



from .parsing_rules import element_comparator
#t = tokenize_text('-hello')
#p = get_mnemonic('-{name}') & DC.Update_Flag('flags', symbol.mnemonic.context.manipulation.discard_entry)


t = tokenize_text('-hello')
p = get_mnemonic('-{name}') & DC.Wrap_Capture('name', lambda x: f'~{x}~')

#t = tokenize_text('hello as thing')
#p = get_mnemonic('{name} as {alias}') & DC.Update_Flag('flags', symbol.mnemonic.context.manipulation.discard_entry)

ec = element_comparator()
print(ec.compare_items(p, t))
print(ec.captures)


exit()

print(
	get_mnemonic('-{name}') | get_mnemonic('+{name}') | get_mnemonic('-{name}')
)


class setup_processor:
	@register_mnemonic_function(processor_setup_processor, 'CTX[:] {pattern}')
	def mnemonic_function(processor_state, pattern):
		print('CTX', pattern)


	@register_mnemonic_function(processor_setup_processor, 'PS[:] {pattern}')
	def mnemonic_function(processor_state, pattern):
		print('PS', pattern)

class amend_processor:

	@register_mnemonic_function(mnemonic_language_processor, 'amend current processor[:]')
	def amend_current_processor(processor_state):
		#TODO we should improve api so we can make a new state while doing adjustments
		ps = processor_state.with_processor(amend_definition_processor)
		ps.context = ps.context.sub_context(dict(target_processor=processor_state))
		ps.process_tree(processor_state.node.body)


	@register_mnemonic_function(amend_definition_processor, 'setup[:]')
	def setup(processor_state):
		ps = processor_state.with_processor(processor_setup_processor)
		ps.context = ps.context.sub_context(dict(target_processor=processor_state))
		ps.process_tree(processor_state.node.body)

	@register_mnemonic_function(amend_definition_processor, 'mnemonic function[:] {pattern}')
	def mnemonic_function(processor_state, pattern):
		target_processor = processor_state.context.require('target_processor')
		register_mnemonic_function(target_processor, pattern, processor_state.node.body)






root_context = context('root', dict(
	# ...
))

mlp = mnemonic_language_processor(state=dict(context=root_context))