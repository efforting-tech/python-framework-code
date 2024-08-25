from efforting.mvp6.mnemonic_language.bootstrap import bootstrap_dispatcher

from efforting.mvp6.document import create_text_tree_document_from_str

test_tree = create_text_tree_document_from_str('''

	mnemonic tree processor: test_processor
		setup:
			all captures

		mnemonic function: greet {pattern as whom}
			return f'Hello {whom}!'


''', normalize_block=True)


#mlp.context.set('hello', 'world')
bootstrap_dispatcher.dispatch_tree(test_tree)

tt2 = create_text_tree_document_from_str('''

	greet World


''', normalize_block=True)


print(bootstrap_dispatcher.state.context['test_processor'].dispatch_node(tt2))	#Hello World!

