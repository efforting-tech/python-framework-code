from efforting.mvp6 import ABC
from efforting.mvp6.context import context, python_code_execution_interface
from efforting.mvp6.document import create_text_tree_document_from_str
from efforting.mvp6.mnemonic_language.mnemonic_captures import cit
from efforting.mvp6.mnemonic_language.mnemonic_tokens_to_pattern import mttp
from efforting.mvp6.mnemonic_language.parser import tp
from efforting.mvp6.mnemonic_language.string_formatting_rules import string_formatter
from efforting.mvp6.mnemonic_language.structures import mnemonic_argument, mnemonic_unwrapper
from efforting.mvp6.processing.text_tree import Mnemonic_Text_Tree_Processor
from efforting.mvp6.record import member as M
from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.text.tree import Text_Tree_Listing


#NEXT UP - more proper bootstrap experiment
#NOTE - maybe we want a common shorthand for the lib, maybe just `lib´

#TODO - we should also figure out how we want to deal with processor state, I don't really like __getattr__ there..

test_tree = create_text_tree_document_from_str('''

	mnemonic function: define tree processor[:] {name}

		print(f'We should define the processor {name!r}')
		print(f'Also, our source is: {__source_code__!r}')

		#register_mnemonic_function()

''', normalize_block=True)

ttp = Mnemonic_Text_Tree_Processor('ttp')	#Text Tree Processor


def get_mnemonic(mnemonic):
	#TODO - use resolver(processor)
	#TODO - do not make assumptions in the conditions below
	if isinstance(mnemonic, tuple):
		return mttp.process_item(mnemonic)
	elif isinstance(mnemonic, str):
		return mttp.process_item(tp.process_text(mnemonic))
	else:
		return mnemonic

@ABC.Decorator
class pending_mnemonic_function_for_processor(Structure):
	processor = M.positional()
	mnemonic = M.positional()

	def __call__(self, function):
		register_mnemonic_function(self.processor, self.mnemonic, function)
		return function

def register_mnemonic_function(processor, mnemonic, function=None):
	mnemonic = get_mnemonic(mnemonic)
	names = tuple(cit(mnemonic))

	if function is None:
		return pending_mnemonic_function_for_processor(processor, mnemonic)
	elif isinstance(function, ABC.Text.Block):	#TODO - ABC.Text.Block should be a subclass of ABC.Text    #TODO  we shoulda also have some neat resolvers for common type conversions so that we can ask for an editable block directly, maybe even higher level semantic types (could be a sub tree within the symbol tree)
		#COMPILE FUNCTION

		b = function.editable_copy()
		b.normalize_block()

		args = ', '.join(('processor_state', *names))
		function_def = f'def handler({args}):'
		python_code = Text_Tree_Listing.from_title_and_branches(function_def, b).to_str()

		#scope = dict()
		#exec(python_code, scope)
		ctx = (processor.context or root_context).sub_context(dict(__source_code__ = python_code))
		tracker = processor.tracker
		python_code_execution_interface.exec_in_context(ctx, python_code, tracker=tracker)

		function = ctx.get('handler')

	elif isinstance(function, str):
		#Make text tree (create_text_tree_document_from_str) but it should be editable
		#TODO - maybe also a symbol based way to create new objects or accessing common functions?
		raise Exception('NI')

	elif callable(function):
		pass
	else:
		#TYPE ERROR
		raise Exception('NI')

	mu = mnemonic_unwrapper(function)
	for n in names:

		if n != 'pattern':
			pp = lambda n: string_formatter().process_item(n)	#TODO - This is now assuming that we do want to turn this to text, which we may not want (we should rely on capture_meta)
		else:
			pp = None

		mu.arguments.append(mnemonic_argument(
			n,
			post_processor = pp,
		))

	processor.register(mnemonic)(mu)



@register_mnemonic_function(ttp, 'mnemonic function[:] {pattern}')
def process_mnemonic(processor_state, pattern):
	register_mnemonic_function(processor_state, pattern, processor_state.node.body)

root_context = context('root', dict(register_mnemonic_function=register_mnemonic_function))

ttp(state=dict(context=root_context)).process_tree(test_tree)


ttp(state=dict(context=root_context)).process_tree(create_text_tree_document_from_str('''

	define tree processor: mahproc


''', normalize_block=True))


