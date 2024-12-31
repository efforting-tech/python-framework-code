from efforting.tech.template1.core.table import Basic_Dict_Table, Basic_Sequence_Table, Function_Formatter

from efforting.tech.template1.core import records as R

#TODO - move into library, somewhere under data stuff
class Object_Mapping_With_Counter(R.Record):
	name_format: R.Field() = '{}'
	index: R.Field() = 0
	lut: R.Field(factory=dict)

	def format(self):
		return self.name_format.format(self.index)

	def map(self, item):
		if (existing := self.lut.get(item)) is not None:
			return existing

		result = self.lut[item] = self.format()
		self.index += 1
		return result

bt = Basic_Sequence_Table('Node Parent Title Span'.split())

N1, N2, N3, N4, N5, N6, N7 = [object() for i in range(7)]

bt.add_row(N1, 	None, 	None, 	(0, 3))
bt.add_row(N2, 	N1, 	None, 	(0, 2))
bt.add_row(N3, 	N2, 	None, 	(0, 0))
bt.add_row(N4, 	N3, 	'a', 	(0, 0))
bt.add_row(N5, 	N2, 	'b', 	(1, 1))
bt.add_row(N6, 	N2, 	'c', 	(2, 2))
bt.add_row(N7, 	N1, 	'd', 	(3, 3))

node_register = Object_Mapping_With_Counter('N{}', 1)

bt.set_column_format(0, Function_Formatter(bt, lambda c: node_register.map(c)))
bt.set_column_format(1, Function_Formatter(bt, lambda c: '-' if c is None else node_register.map(c)))
bt.set_column_format(2, Function_Formatter(bt, lambda c: '-' if c is None else repr(c)))
bt.set_column_format(3, Function_Formatter(bt, lambda c: f'{c[0]}..{c[1]}'))

print(bt.format())