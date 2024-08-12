from efforting.mvp6.mnemonic_language.bootstrap import mlp
from efforting.mvp6.mnemonic_language import bootstrap as BS
from efforting.mvp6.document import create_text_tree_document_from_str

#TODO - I want to redo the context setup a bit so it can encode more compldex expressions and maybe later include factories and stuff - also nice if we can determine which things to export back to the context
#		one nice thing would be to be able to shorthand stuff like ps = processor_state.with_processor(processor_registry['amend_definition_processor'])



processor_registry = dict(
	mnemonic_language_processor = BS.mnemonic_language_processor,
	amend_definition_processor = BS.amend_definition_processor,
	processor_setup_processor = BS.processor_setup_processor,
	context_manipulation_processor = BS.context_manipulation_processor,
)


from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M


test_tree = create_text_tree_document_from_str('''



''', normalize_block=True)


mlp.context.set('processor_registry', processor_registry)
mlp.context.set('pending_record', pending_record)
mlp.context.set('BS', BS)
mlp.context.set('M', M)

mlp.process_tree(test_tree)

print(mlp.context.locals['template'](123))