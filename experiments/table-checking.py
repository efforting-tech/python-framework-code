from efforting.tech.template1.core.table import Basic_Dict_Table, Basic_Sequence_Table, Function_Formatter
from efforting.tech.template1.core.table.condition import Continuous_Unordered_Format_And_Match_Table_Proxy, Continuous_Format_And_Match_Table_Proxy
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


def create_node_table():
	node_register = Object_Mapping_With_Counter('N{}', 1)
	bt = Basic_Sequence_Table('Node Parent Title Span'.split())
	bt.set_column_format(0, Function_Formatter(bt, lambda c: node_register.map(c)))
	bt.set_column_format(1, Function_Formatter(bt, lambda c: '-' if c is None else node_register.map(c)))
	bt.set_column_format(2, Function_Formatter(bt, lambda c: '-' if c is None else repr(c)))
	bt.set_column_format(3, Function_Formatter(bt, lambda c: f'{c[0]}..{c[1]}'))
	#bt.table_formatter.use_middle_divider = True
	return bt


bt = create_node_table()

N1, N2, N3, N4, N5, N6, N7 = [object() for i in range(7)]

bt.add_row(N1, 	None, 	None, 	(0, 3))
bt.add_row(N2, 	N1, 	None, 	(0, 2))
bt.add_row(N3, 	N2, 	None, 	(0, 0))
bt.add_row(N4, 	N3, 	'a', 	(0, 0))
bt.add_row(N5, 	N2, 	'b', 	(1, 1))
bt.add_row(N6, 	N2, 	'c', 	(2, 2))
bt.add_row(N7, 	N1, 	'd', 	(3, 3))

# NOTE - This was a failed experiment in unordered comparison. The problem though is that The values in the node and parent columns will not be the same
#		currently I don't have a strategy for resolving this.

# #This one is out of order
# bt3 = Continuous_Unordered_Format_And_Match_Table_Proxy(bt, create_node_table())	#Defaults to key = 0

# bt3.add_row(N1, 	None, 	None, 	(0, 3))
# bt3.add_row(N2, 	N1, 	None, 	(0, 2))
# bt3.add_row(N6, 	N2, 	'c', 	(2, 2))
# bt3.add_row(N7, 	N1, 	'd', 	(3, 3))
# bt3.add_row(N3, 	N2, 	None, 	(0, 0))
# bt3.add_row(N4, 	N3, 	'a', 	(0, 0))
# bt3.add_row(N5, 	N2, 	'b', 	(1, 1))


#Create another table using other references
O1, O2, O3, O4, O5, O6, O7 = [object() for i in range(7)]

bt2 = Continuous_Format_And_Match_Table_Proxy(bt, create_node_table())
bt2.add_row(O1, None, 	None, 	(0, 3))
bt2.add_row(O2, O1, 	None, 	(0, 2))
bt2.add_row(O3, O2, 	None, 	(0, 0))
bt2.add_row(O4, O3, 	'b', 	(0, 0))


