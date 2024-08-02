
# #NOTE - this pattern can be used to create closures that we can use for passing in values not suitable to be passed in as text (of course we could also pass it in as positional arguments)
# def outer():
# 	value = None

# 	def some_func():
# 		print(value)

# 	return some_func

# sf = outer()

# sf.__closure__[0].cell_contents = 'Hello'

# sf()

# print(sf)


from efforting.mvp6 import symbol
from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.matching import data_condition as DC
from efforting.mvp6.mnemonic_language.mnemonic_tokens_to_pattern import mttp
from efforting.mvp6.mnemonic_language.parser import tp
from efforting.mvp6.mnemonic_language.parsing_rules import element_comparator
from efforting.mvp6.mnemonic_language.rudimentary_definition_helpers import join_sequence, word, optional, literal, ws
from efforting.mvp6.mnemonic_language.structures import Optional, Mnemonic, Expression
from efforting.mvp6.mnemonic_language.styling_rules import styling_processor
from efforting.mvp6.mnemonic_language.string_formatting_rules import string_formatter
from efforting.mvp6.mnemonic_language.mnemonic_captures import cit
from efforting.mvp6.processing.text_tree import Mnemonic_Text_Tree_Processor
from efforting.mvp6.processing.generic import Type_LUT_Iterator
from efforting.mvp6.text.styling import presets as SP
from efforting.mvp6.text.styling.terminal import render_styled_text
from efforting.mvp6.text import Line_Listing
from efforting.mvp6.text.tree import Text_Tree_Listing
from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M




class mnemonic_argument(Structure):
	name = M.positional()
	post_processor = M.positional(None)

	def acquire(self, processor_state):
		if self.post_processor:
			return self.post_processor(processor_state.captures[self.name])
		else:
			return processor_state.captures[self.name]

class mnemonic_unwrapper(Structure):
	function = M.positional()
	arguments = M.positional(factory=list)

	def __call__(self, processor_state):
		return self.function(processor_state, *(arg.acquire(processor_state) for arg in self.arguments))


#TODO - move to data utils
def unpack_dict(target, *keys):
	yield from (target[k] for k in keys)


test_tree = create_text_tree_document_from_str('''

	mnemonic function: define tree processor[:] {name}

		print(f'We should define the processor {name!r}')

''', normalize_block=True)

ttp = Mnemonic_Text_Tree_Processor('ttp')	#Text Tree Processor



@ttp.register('mnemonic function[:] {pattern}')
def process_mnemonic(processor_state):
	[pattern] = unpack_dict(processor_state.captures, 'pattern')
	mnemonic = mttp.process_item(pattern)



	names = tuple(cit(mnemonic))
	assert (len(names) <= 1) or (len(set(names)) == len(names))	#If there are more than one, make sure there are no duplicates

	#TODO - make sure that we know how to handle each of the captures (we will use capture_meta for it)
	#TODO - we must be able to couple functions and additional code - either by turning the expression into code or by creating unique slots we can access (closure?)
	#TODO - investigage if we can use closures alltogether (it is possible (see above))
	#		but we may instead opt to use a wrapper that does the preprocessing before calling the user function
	#unpack_line = f'[{unpack_to}] = [{unpack_from}]'

	b = processor_state.node.body.editable_copy()
	b.normalize_block()
	#b.insert_line(unpack_line)

	args = ', '.join(('processor_state', *names))
	function_def = f'def handler({args}):'
	python_code = Text_Tree_Listing.from_title_and_branches(function_def, b).to_str()

	#TODO - use context system
	scope = dict()
	exec(python_code, scope)
	mu = mnemonic_unwrapper(scope['handler'])

	for n in names:
		mu.arguments.append(mnemonic_argument(
			n,
			post_processor = lambda n: string_formatter().process_item(n)	#TODO - This is now assuming that we do want to turn this to text, which we may not want (we should rely on capture_meta)
		))




	#string_formatter().process_item(processor_state.captures[{n!r}])

	processor_state.register(mnemonic)(mu)



	#Here we must process pattern and translate things.
	#For instance {pattern} should be turned to DC.Capture_Remaining('pattern') while {name} should be word() & DC.Capture('name'),



ttp().process_tree(test_tree)

ttp().process_tree(create_text_tree_document_from_str('''

	define tree processor: mahproc


''', normalize_block=True))


