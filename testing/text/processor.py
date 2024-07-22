from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.text.tree.processor import Processor


T = create_text_tree_document_from_str('''

	title: Test everything

	include modules: abc, basic


''', normalize_block=True)

P = Processor()

P.rules.add_mnemonic_rule('title: {remaining as title}')



#P.process_node(next(T.iter_nodes()))