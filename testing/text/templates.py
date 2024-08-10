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

class pending_record(Structure):
	name = M.positional()
	bases = M.positional(factory=lambda: [Structure])
	members = M.positional(factory=dict)

test_tree = create_text_tree_document_from_str('''

	amend current processor:
		setup:
			CPT: name
			PS: node

			#Note that CTX is not needed in the current implementation but we probably will want it later
			CTX: processor_registry, BS


		mnemonic function: amend processor[:] {name}
			#TODO we should improve api so we can make a new state while doing adjustments
			ps = processor_state.with_processor(processor_registry['amend_definition_processor'])

			ps.context = ps.context.sub_context(dict(
				target_processor=processor_state.with_processor(processor_registry[name]),
				pending_mnemonic_implementation = BS.pending_mnemonic_implementation(),
			))

			ps.process_tree(node.body)



	amend current processor:
		setup:
			CPT: name
			CTX: processor_registry, pending_record
			PS: node, context

		mnemonic function: define record[:] {name}
			#TODO - support bases
			ps = processor_state.with_processor(processor_registry['record_definition_processor'])

			new_record = pending_record(name)

			ps.context = ps.context.sub_context(dict(
				target_record = new_record,
			))

			ps.process_tree(node.body)

			context.set(name, type(new_record.name, tuple(new_record.bases), new_record.members))


		mnemonic function: create processor[:] {name}
			new_processor = processor_registry[name] = BS.Mnemonic_Text_Tree_Processor(name)

			ps = processor_state.with_processor(processor_registry['amend_definition_processor'])

			ps.context = ps.context.sub_context(dict(
				target_processor = processor_state.with_processor(new_processor),
				pending_mnemonic_implementation = BS.pending_mnemonic_implementation(),
			))

			ps.process_tree(node.body)


	create processor: record_definition_processor
		setup:
			CPT: name, init
			CTX: processor_registry, target_record
			PS: node

		mnemonic function: P {name}{pattern as init}
			#TODO - support interpreting init expressions
			assert not init, 'init not supported yet'
			target_record.members[name] = M.positional()

	define record: template
		P stuff



''', normalize_block=True)


mlp.context.set('processor_registry', processor_registry)
mlp.context.set('pending_record', pending_record)
mlp.context.set('BS', BS)
mlp.context.set('M', M)

mlp.process_tree(test_tree)

print(mlp.context.locals['template'](123))