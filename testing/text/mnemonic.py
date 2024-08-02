from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.mnemonic_language.mnemonic_tokens_to_pattern import mttp
from efforting.mvp6.mnemonic_language.string_formatting_rules import string_formatter
from efforting.mvp6.mnemonic_language.mnemonic_captures import cit
from efforting.mvp6.processing.text_tree import Mnemonic_Text_Tree_Processor
from efforting.mvp6.text.tree import Text_Tree_Listing
from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M

#TODO - move to proper place in mnemonic_language
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

	b = processor_state.node.body.editable_copy()
	b.normalize_block()

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

	processor_state.register(mnemonic)(mu)


ttp().process_tree(test_tree)

ttp().process_tree(create_text_tree_document_from_str('''

	define tree processor: mahproc


''', normalize_block=True))


