from efforting.mvp6.mnemonic_language.bootstrap import mlp
from efforting.mvp6.document import create_text_tree_document_from_str

test_tree = create_text_tree_document_from_str('''

	amend current processor:
		setup:
			PS: node, captures as cpt
			CTX: hello
			MSYS: -processor_state, processor_state as PS
			CPT: thing

		mnemonic function: test {name as thing}
			print('THING', thing)
			print(dir())	#'PS', 'cpt', 'hello', 'node', 'thing'
			print(cpt)		#{'thing': 'stuff'}

		setup:
			PS: -node

		mnemonic function: test2 {name as thing}
			print(dir())	#'PS', 'cpt', 'hello', 'thing'


	test stuff
	test2 stuff

''', normalize_block=True)


mlp.context.set('hello', 'world')
mlp.process_tree(test_tree)

