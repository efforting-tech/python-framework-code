from .. import Symbol as S
from ..core import record as R
#from ..core.symbol import Enum as E
from ..core.dispatcher import Regex_Transformer
from ..core.dispatcher.mnemonic_language import patterns as PAT
from ..core.dispatcher.tree_view import Tree_View_Regex_Dispatcher
from .patterns import macro_pattern
from ..core.text import Immutable_Tree_View
from .import parser
from . import mnemonic_ast as MAST


class Tree_Processor(R.Record):
	result: R.Field(kind=S.Member.Kind.Internal)

	def __init__(self, content):
		super().__init__()
		self.result = self.process_tree(Immutable_Tree_View.from_anything(content))

	def process_tree(self, node):
		return self.D.bound_dispatch_tree(self, node)


class Inline_Processor(R.Record):
	result: R.Field(kind=S.Member.Kind.Internal)

	def __init__(self, content):
		super().__init__()
		self.result = self.D.bound_dispatch_item(self, content)



class Inline_Macro_Processor(Inline_Processor):
	D = Regex_Transformer()

	@D.register_function(PAT.words('current function'))
	def handle_include(self):
		return MAST.Well_Known.Current_Function



class Macro_Processor(Tree_Processor):
	D = Tree_View_Regex_Dispatcher()

	@D.register_function(macro_pattern(PAT.pattern, 'include'))
	def handle_include(self, dispatcher, node, match):
		[path] = match.value.match.groups()
		return MAST.Include(path)

	@D.register_function(macro_pattern(PAT.pattern, 'emit'))
	def handle_include(self, dispatcher, node, match):
		[path] = match.value.match.groups()
		return MAST.Emit(path)


class Macro(Tree_Processor):
	D = Tree_View_Regex_Dispatcher()

	@D.register_function(r'§.*')
	def handle_anything(self, dispatcher, node, match):
		return Macro_Processor(node).result

	@D.register_function(r'.*')
	def handle_default(self, dispatcher, node, match):

		title = list()
		for title_piece in parser.parse_wrapped(node.title):
			match title_piece:
				case parser.text(text):
					title.append(text)

				case parser.wrapped(text):
					title.append(Inline_Macro_Processor(text).result)

				case unhandled:
					raise Exception(unhandled)

		return MAST.Tree(title, self.process_tree(node.body))