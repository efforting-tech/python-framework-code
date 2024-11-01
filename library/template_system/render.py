from ..core import symbol
from ..core import record as R
from ..core.dispatcher import Type_LUT_Processor, ID_LUT_Processor, Type_LUT_Reducer

from .. import Symbol as S

from ..core.dispatcher.aggregation import Result_List
from . import mnemonic_ast as MAST


class Level_Tracker_Context(R.Record):
	level: R.Field() = 0

	def __enter__(self):
		self.level += 1

	def __exit__(self, et, ev, tb):
		self.level -= 1

class Synth:
	OP = symbol.Enum('OP',
		'Start_of_Line',
		'End_of_Line',
	)

	class Write_Str(R.Record):
		value: R.Field() = None

	class Write_Tree(R.Record):
		value: R.Field() = None

	class Set_Indention_Level(R.Record):
		value: R.Field() = 0


class Synthesizer(R.Record):
	result: R.Field(factory=list)
	indention_level: R.Field(factory=Level_Tracker_Context)
	last_used_indention_level: R.Field() = 0

	def indented_context(self):
		return self.indention_level

	def check_indent(self):
		if self.indention_level.level != self.last_used_indention_level:
			self.last_used_indention_level = self.indention_level.level
			self.result.append(Synth.Set_Indention_Level(self.indention_level.level))

	def start_line(self):
		self.check_indent()
		self.result.append(Synth.OP.Start_of_Line)

	def end_line(self):
		self.result.append(Synth.OP.End_of_Line)

	def write_str(self, text):
		self.check_indent()
		self.result.append(Synth.Write_Str(text))

	def write_tree(self, text):
		self.check_indent()
		self.result.append(Synth.Write_Tree(text))

class Renderer(R.Record):
	result: R.Field(factory=Synthesizer)
	context: R.Field(factory=dict)
	#stack: R.Field(factory=

	D = Type_LUT_Processor()
	LD = Type_LUT_Processor()	#Line renderer
	LDWS = ID_LUT_Processor()

	@LDWS.register_function(MAST.Well_Known.Current_Function)	#This is just an example
	def process_wks(self, wks):
		self.result.write_str('DEMO')


	@LD.register_function(symbol.Enum_Identity)
	def process_item(self, item):
		self.LDWS.bound_dispatch_item(self, item)

	@LD.register_function(str)
	def process_item(self, item):
		self.result.write_str(item)

	@D.register_function(Result_List)
	def process_item(self, item):
		self.D.bound_dispatch_sequence(self, item.value)

	@D.register_function(MAST.Include)
	def process_item(self, item):
		print('Should import', item.path)
		#self.D.bound_dispatch_item(self, item.body)

	@D.register_function(MAST.Emit)
	def process_item(self, item):
		self.result.write_tree(self.resolve(item.path))

	@D.register_function(MAST.Tree)
	def process_item(self, item):
		self.result.start_line()
		self.LD.bound_dispatch_sequence(self, item.title)
		self.result.end_line()

		with self.result.indented_context():
			self.D.bound_dispatch_item(self, item.body)

	def resolve(self, name):
		return self.context[name]

	def render(self, item):
		self.D.bound_dispatch_item(self, item)





#TODO - name these better
class Renderer2(R.Record):
	current_line: R.Field(factory=list)
	current_block: R.Field(factory=list)
	indention_level: R.Field() = 0


	#NOTE - one drawback of having D be a class attribute is that we can't derive thie dispatcher - I think we should declare D as a special field that understands hierarchy.
	D: R.Field(kind=S.Member.Kind.Hierarchial) = Type_LUT_Processor()

	LDWS = ID_LUT_Processor()
	Line_Reducer = Type_LUT_Reducer()
	Block_Reducer = Type_LUT_Reducer()

	#NOTE - one big drawback with this way of defining things is that we create a bunch of littering functions here but if we throw it all in a class _dispatch_table then the decorators fail to resolve
	@Line_Reducer.register_function(str, str)
	def reduce(a, b):
		return f'{a}{b}'

	@Block_Reducer.register_function(str, str)
	def reduce(a, b):
		return f'{a}\n{b}'


	@LDWS.register_function(Synth.OP.Start_of_Line)
	def process_wks(self, wks):
		assert self.is_at_start_of_line()
		self.current_line.append('\t' * self.indention_level)

	@LDWS.register_function(Synth.OP.End_of_Line)
	def process_wks(self, wks):
		self.current_block.append(self.Line_Reducer.reduce_sequence( self.current_line ))
		self.current_line.clear()

	@D.register_function(symbol.Enum_Identity)
	def process_item(self, item):
		self.LDWS.bound_dispatch_item(self, item)

	@D.register_function(Synth.Write_Str)
	def process_item(self, item):
		self.current_line.append(item.value)


	@D.register_function(Synth.Write_Tree)
	def process_item(self, item):
		assert self.is_at_start_of_line()
		#print('Write tree', repr(item.value.copy(adjust_indent=self.indention_level).to_str()))
		self.current_block.append(item.value.copy(adjust_indent=self.indention_level).to_str())


	@D.register_function(Synth.Set_Indention_Level)
	def process_item(self, item):
		self.indention_level = item.value

	@D.register_function(list)
	@D.register_function(tuple)
	def process_item(self, seq):
		self.D.bound_dispatch_sequence(self, seq)

	def is_at_start_of_line(self):
		return len(self.current_line) == 0


	def render_sequence(self, seq):
		self.D.bound_dispatch_sequence(self, seq)

	def render_block(self, item):
		assert not self.current_block
		self.D.bound_dispatch_item(self, item)
		return self.Block_Reducer.reduce_sequence(self.current_block)




# tlr = Type_LUT_Reducer()

# @tlr.register_function(int, int)
# @tlr.register_function(str, str)
# def f(a, b):
# 	return a + b


# print(tlr.reduce_sequence( ['hello', 'world', 123, 456, 'zup?', 'all good?'] ))
# # ['helloworld', 579, 'zup?all good?']
# print(tlr.reduce_sequence( ['hello', 'world', 'zup?', 'all good?'] ))
# # helloworldzup?all good?

