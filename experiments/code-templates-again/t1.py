#This experiment initially will deal with planning and documentation but we will get to templating

from efforting.mvp4 import type_system as RTS
from efforting.mvp4.text_processing.improved_text_node_processor import improved_text_node_processor
from efforting.mvp4.rudimentary_features.code_manipulation.templating.pp_context import context
from efforting.mvp4.text_processing.improved_tokenization import regex_parser

import command_pattern_processor
import local_types as T
import re
local_context = context.from_this_frame()

class improved_tree_node_processor(improved_text_node_processor):
	pattern_processor = RTS.setting(regex_parser)
	context = RTS.setting(local_context)
	post_processor = RTS.setting(lambda x: T.document(*x))

	@RTS.setting
	def pattern_processor(pattern):
		inner = command_pattern_processor.command_pattern_processor.process_text(pattern).to_pattern()
		return re.compile(rf'^{inner}$', re.I)



c_implementation_processor = improved_tree_node_processor.from_raster('''

	pattern									action
	-------									------
	SOURCE[:] {name...}						return T.c_source(name, *P.process_tree_iteratively(N.body))
	HEADER[:] {name...}						return T.c_header(name, *P.process_tree_iteratively(N.body))

	INCLUDES[:] {includes...}				return T.c_includes.from_anything(includes, N.body)
	INCLUDES[:]	 							return T.c_includes.from_anything(N.body)

	RAW INCLUDES[:]	 						return T.c_includes.from_raw(*N.body.lines)

''')




named_option_processor  = improved_tree_node_processor.from_raster('''

	pattern									action
	-------									------
	· {name...}								return T.named_option(name, *P.context.accessor.parent_processor.process_tree_iteratively(N.body))

''', default_action = 'return P.context.accessor.parent_processor.process_text(M.text)')


def with_parent_processor(parent, processor, result):
	#This is a bit of a hack, result is a generator so we can manipulate processor before asking for results
	#We should probably find a better way
	with processor.context.stack(parent_processor=parent):
		return tuple(result)




command_specification_processor = improved_tree_node_processor.from_raster('''

	pattern									action
	-------									------
	NOTE[:] {text...}						return T.note(text, N.body)
	NOTE[:]									return T.note(None, N.body)

	EXAMPLES[:] {text...}					return T.examples(text, N.body)
	EXAMPLES[:]								return T.examples(None, N.body)

	INCLUDE[:] {filename...}				return T.include_tree.from_anything(filename, N.body)
	INCLUDE[:]								return T.include_tree.from_anything(N.body)

	BRIEF[:] {text...}						return T.brief(text, N.body)
	BRIEF[:]								return T.brief(None, N.body)

	PURPOSE[:] {text...}					return T.purpose(text, N.body)
	PURPOSE[:]								return T.purpose(None, N.body)

	GROUP[:] {name...}						return T.group(name, *P.process_tree_iteratively(N.body))
	CONCEPT[:] {name...}					return T.concept(name, *P.process_tree_iteratively(N.body))
	FEATURE[:] {name...}					return T.feature(name, *P.process_tree_iteratively(N.body))

	STRUCTURE TABLE[:] {name...}			return T.structure_table(name, N.body)	#TODO should parse table
	STRUCTURE[:] {name...}					return T.structure(name, *P.process_tree_iteratively(N.body))


	MODE OF {type...}: {name...}			return T.mode_of_type(type, name, *with_parent_processor(P, named_option_processor, named_option_processor.process_tree_iteratively(N.body)))
	LIST OF {type...}: {name...}			return T.list_of_type(type, name, *with_parent_processor(P, named_option_processor, named_option_processor.process_tree_iteratively(N.body)))

	INTRODUCTION[:]							return T.introduction(T.text(N.body))

	REQUIRED FEATURES[:] {features...}		return T.required_features.from_anything(features, N.body)
	REQUIRED FEATURES[:]	 				return T.required_features.from_anything(N.body)

	C IMPLEMENTATION[:] {name...}			return T.c_implementation(name, *c_implementation_processor.process_tree_iteratively(N.body))
	C IMPLEMENTATION[:]	 					return T.c_implementation(None, *c_implementation_processor.process_tree_iteratively(N.body))

''')




def dump(item, indent=''):
	match item:
		case type():
			print(f'{indent}{item!r}')
		case _:
			print(f'{indent}{item!r}')
			if members := getattr(item, 'members', None):
				for member in members:
					dump(member, f'{indent}  ')

def load_tree(path):
	document = command_specification_processor.process_path(path)
	return T.loaded_tree(path, *document.members)

result = load_tree('planning/camera.treedef')
dump(result)
