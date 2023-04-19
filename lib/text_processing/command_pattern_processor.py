from ..rudimentary_features.code_manipulation.templating.pp_context import context
from .improved_tokenization import bootstrap_action_processor_table, bootstrap_action_processor_context, extended_tokenizer, bootstrap_processor
from ..iteration_utils import single_item
from . import command_pattern_types as CPT

local_context = context.from_this_frame()

local_context.update(bootstrap_action_processor_context)
bootstrap_action_processor = bootstrap_processor.from_table(bootstrap_action_processor_table, context=local_context)

capture_options = extended_tokenizer.from_raster(bootstrap_action_processor.process_text, r'''

	type		pattern				action
	----		-------				------
	regex		(\w+)				return CPT.option(*M.positional)
	literal		|					skip
	regex		\s+					skip

''')

command_pattern_processor_capture_specifics = extended_tokenizer.from_raster(bootstrap_action_processor.process_text, r'''

	type		pattern				action
	----		-------				------
	regex		\*(\w+)\?			return CPT.remaining_words(*M.positional, greedy=False)
	regex		(\w+)\.\.\.\?		return CPT.remaining_text(*M.positional, greedy=False)

	regex		\*(\w+)				return CPT.remaining_words(*M.positional)
	regex		(\w+)\.\.\.			return CPT.remaining_text(*M.positional)

	regex		(\w+)				return CPT.specific_word(*M.positional)
	regex		\.(\w+)				return CPT.specific_dotted_identifier(*M.positional)

''', post_processor=single_item)

command_pattern_processor_capture = extended_tokenizer.from_raster(bootstrap_action_processor.process_text, r'''

	type		pattern				action
	----		-------				------
	regex		([^}]+):([^}]+)		return CPT.specified_capture(command_pattern_processor_capture_specifics.process_text(M.pending_positional), *capture_options.process_text(M.pending_positional))
	regex		([^}]+)				return command_pattern_processor_capture_specifics.process_text(M.pending_positional)
	literal		}					leave

''', post_processor=single_item)

command_pattern_processor_optional = extended_tokenizer.from_raster(bootstrap_action_processor.process_text, r'''

	type		pattern				action
	----		-------				------
	literal		]					leave

''', post_processor=lambda item: CPT.optional(CPT.sequential_pattern(*item)))

command_pattern_processor = extended_tokenizer.from_raster(bootstrap_action_processor.process_text, r'''

	type		pattern				action
	----		-------				------
	literal		[					enter command_pattern_processor_optional
	literal		{					enter command_pattern_processor_capture
	regex		\s+					return CPT.required_space()

''', default_action='return CPT.literal_text(_)', post_processor=lambda x: CPT.sequential_pattern(*x))

command_pattern_processor_optional.extend(command_pattern_processor)
