from .create_function import create_function
import ast
# def matching_rule(expression):
# 	code = f'match var:\n\tcase {expression}:\n\t\tresult'

# 	match ast.parse(code):
# 		case ast.Module(body=[ast.Match(cases=[case])]):
# 			if case.guard:
# 				print(f'{ast.unparse(case.pattern)} if {ast.unparse(case.guard)}')
# 			else:
# 				print(ast.unparse(case.pattern))

#TODO - use caching for all these?
def create_matching_function(pattern, name='check_match', item_arg='item', stack_offset=0):
	return create_function(name, item_arg,
		f'match {item_arg}:\n'
		f'	case {pattern}:\n'
		f'		return True\n'
		f'return False\n',
		stack_offset = stack_offset + 1,
	)

def create_extracting_function(pattern, stack_offset=0):
	return create_function('pattern_based_extractor', '_item',
		f'match _item:\n'
		f'	case {pattern}:\n'
		f'		return {{k: v for k, v in locals().items() if not k.startswith("_")}}\n',
		stack_offset = stack_offset + 1,
	)

CHECK_MATCH_CACHE = dict()
def check_match(pattern, item):
	if not (f := CHECK_MATCH_CACHE.get(pattern)):
		f = CHECK_MATCH_CACHE[pattern] = create_matching_function(pattern, stack_offset=1)
	return f(item)

#Do we want this?
def get_matching_ast(expression):
	code = f'match var:\n\tcase {expression}:\n\t\tresult'
	match ast.parse(code):
		case ast.Module(body=[ast.Match(cases=[case])]):
			return case

	raise Exception()