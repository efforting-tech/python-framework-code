from ...type import record as R
from ...abc import ABC
from ... import typing as TY


class Pending_Core_Type_Conversion_Entry:
	def __init__(self, converter, source_type, target_type):
		self.converter = converter
		self.source_type = source_type
		self.target_type = target_type

	def __call__(self, function):
		self.converter.lut[self.source_type, self.target_type] = function
		return function


class Core_Type_Converter:
	def __init__(self):
		self.lut = dict()

	def register(self, source_type, target_type):
		return Pending_Core_Type_Conversion_Entry(self, source_type, target_type)


	def convert(self, value, target_type):
		lut_key = type(value), target_type
		return self.lut[lut_key](value)


main_converter = Core_Type_Converter()

@main_converter.register(list, TY.Sequence(ABC.Text.Line.Immutable))
def load(source):
	return tuple(main_converter.convert(e, ABC.Text.Line.Immutable) for e in source)

@main_converter.register(str, ABC.Text.Line.Immutable)
def load(source):
	return Immutable_Line.from_str(source)


class Core_Line_Record(R.Record):
	text: 			R.Field(ensure_type=str)


@ABC.Text.Line.Immutable
class Immutable_Line(Core_Line_Record):
	text: 			R.Field_Update(ensure_type=str, mutable=False)

@ABC.Text.Line.Mutable
class Mutable_Line(Core_Line_Record):
	text: 			R.Field_Update(ensure_type=str, mutable=True)

class Core_Line_View_State(R.Record):
	lines: 			R.Field(type=TY.Sequence(ABC.Text.Line), ensure_type=main_converter)


class Immutable_Line_View_State(Core_Line_View_State):
	lines: 			R.Field_Update(type=TY.Sequence(ABC.Text.Line.Immutable))

class Mutable_Line_View_State(Core_Line_View_State):
	lines: 			R.Field_Update(type=TY.Sequence(ABC.Text.Line.Mutable))


