import subprocess
from ..development_utils import use_linecache_traceback
use_linecache_traceback()

from ..data_utils import attribute_stack
from ..rudimentary_features.code_manipulation.templating.context2 import context3
from ..rudimentary_features.code_manipulation.templating.source_tracker import source_tracker
from ..text_nodes import text_node
from ..text_processing import improved_tokenization as IT
from ..text_processing.command_pattern_processor import command_pattern_processor
from ..text_processing.improved_tokenization import extended_tokenizer
from ..text_processing.mnemonic_tree_processor import mnemonic_tree_processor
from ..text_processing.re_tokenization import SKIP
from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_processing.improved_text_node_processor import A
from ..table_processing.table import table

import re
generic_context = context3.from_this_frame(tracker = source_tracker())

class F:
	def iter_title_body(node):
		for n in node.body.iter_nodes():
			yield n.title, n.body.dedented_copy()

	def csl(text):
		return tuple(t.strip() for t in text.split(','))

	from ..type_system.features import get_settings, get_settings_from_instance
	from ..text_processing.mnemonic_tree_processor import check_cell_in_column, is_empty


#DEPRECATE
processor_def = mnemonic_tree_processor.from_raster_table2('''

	mnemonic								function
	--------								--------
	mnemonic: {mnemonic...}					mnemonic_pattern = command_pattern_processor.process_text(mnemonic.strip())
											function = C.create_bound_function_from_snippet(N.body.text, 'C', 'CX', 'P', 'M', 'N', *(c.name for c in mnemonic_pattern.iter_captures()), allow_clobbering=True)
											CX.target_processor.rules.append((re.compile(rf'^{mnemonic_pattern.to_pattern()}$', re.I), A.call_function_with_accessor(function)))

	default:								#todo - check if default is set
											function = C.create_bound_function_from_snippet(N.body.text, 'C', 'CX', 'P', 'M', 'N')
											CX.target_processor.default_action = A.call_function_with_accessor(function)

''', context=generic_context, strip_raster_cells=False)

#DEPRECATE
generic_main_processor = mnemonic_tree_processor.from_raster_table2('''

	mnemonic								function
	--------								--------
	processor[:] {.name}					sub_context = C.sub_context(name)
											new_processor = mnemonic_tree_processor(include_blanks=True, empty_action='return text_node(("",))', context=sub_context)
											sub_context.locals.update(target_processor=new_processor)

											with attribute_stack(processor_def, context=sub_context):
												processor_def.process_tree(N.body)

											return C.set_and_return(name, new_processor)

	execute in new context[:] {.name}		sub_context = C.sub_context(name)
											sub_context.exec_expression(N.body.text)
											return C.set_and_return(name, sub_context.accessor)

	execute as function[:]					return C.create_bound_function_from_snippet(N.body.text, 'C', 'CX', 'P', 'N')(C, CX, P, N)

	execute[:]								C.exec_expression(N.body.text, C=C, CX=CX, P=P)



''', strip_raster_cells=False, context=generic_context)



processor_def2 = mnemonic_tree_processor.from_raster_table2('''

	mnemonic								function
	--------								--------
	mnemonic: {mnemonic...}					TP = P.target_processor
											sub_context = TP.context.stacked_context(P=TP, C=TP.context, CX=TP.context.accessor)
											return TP.add_contextual_mnemonic_function(sub_context, mnemonic, N.body.text)

	regex: {regex...}						TP = P.target_processor
											sub_context = TP.context.stacked_context(P=TP, C=TP.context, CX=TP.context.accessor)
											return TP.add_contextual_regex_function(sub_context, regex, N.body.text)

	default:								TP = P.target_processor
											sub_context = TP.context.stacked_context(P=TP, C=TP.context, CX=TP.context.accessor)
											return TP.add_contextual_default_function(sub_context, N.body.text)



''', context=generic_context, strip_raster_cells=False, name='processor_def2')


#NOTE - we are actually attribute stacking the processor rather than its context. This may be a bad idea if we are using the
#		same processor in multiple contexts and we should decide how we want to do this and do it better.
#		maybe it would be better to have some shorthand for accessing attributes within the context.
#
#		Maybe we should not put it inside the locals of the context
#		it may be less namespace pollution if we have a specific attribute for the current state
#		that is separate from the context that in many cases will represent the contents of something rather than its state.

#NOTE - this probably would be better suited to use a text_tree at this point - we should convert it
generic_main_processor2 = mnemonic_tree_processor.from_raster_table2('''

	mnemonic											function
	--------											--------
	amend processor[:] {.name}							with attribute_stack(processor_def2, target_processor=C.get(name)):
															return processor_def2.process_tree(N.body)

	amend processor[:]									with attribute_stack(processor_def2, target_processor=P):
															return processor_def2.process_tree(N.body)

	define tree processor[:] {.name}					new_processor = P.empty_copy(name=name)
														with attribute_stack(processor_def2, target_processor=new_processor):
															result = processor_def2.process_tree(N.body)
														C.set(name, new_processor)
														return result

	execute[:]											C.exec_as_function(N.body.text, C=C, CX=CX, P=P, F=F)

	contextual execute[:]								C.exec_in_context(N.body.text, C=C, CX=CX, F=F)

	extend processors by {.extension}: {targets...}		source_processor = C.require(extension)
														for target_processor in map(C.require, F.csl(targets)):
															target_processor.rules.extend(source_processor.rules)



''', strip_raster_cells=False, context=generic_context, name='generic_main_processor2')
