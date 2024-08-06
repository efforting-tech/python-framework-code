from .. import ABC
from ..context import python_code_execution_interface
from ..record import member as M
from ..record.base.public import Structure
from ..text.tree import Text_Tree_Listing
from .mnemonic_captures import cit
from .mnemonic_tokens_to_pattern import mttp
from .parser import tp
from .structures import mnemonic_argument, mnemonic_unwrapper


#TODO - move to proper place
@ABC.Decorator
class pending_mnemonic_function_for_processor(Structure):
	processor = M.positional()
	mnemonic = M.positional()

	def __call__(self, function):
		register_mnemonic_function(self.processor, self.mnemonic, function)
		return function



#TODO - move to proper place
def tokenize_text(text):
	#TODO - use resolver(processor)
	if isinstance(text, tuple):
		return text
	elif isinstance(text, str):
		return tp.process_text(text)
	else:
		raise Exception()

#TODO - move to proper place
def get_mnemonic(mnemonic):		#TODO rename to get_mnemonic_pattern?
	#TODO - use resolver(processor)
	#TODO - do not make assumptions in the conditions below
	if isinstance(mnemonic, tuple):
		return mttp.process_item(mnemonic)
	elif isinstance(mnemonic, str):
		return mttp.process_item(tp.process_text(mnemonic))
	else:
		return mnemonic


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

		#TODO - since we have now added Wrap_Capture we could possibly get rid of this and use that instead
		if n != 'pattern':
			pp = lambda n: string_formatter().process_item(n)	#TODO - This is now assuming that we do want to turn this to text, which we may not want (we should rely on capture_meta)
		else:
			pp = None

		mu.arguments.append(mnemonic_argument(
			n,
			post_processor = pp,
		))

	processor.register(mnemonic)(mu)


