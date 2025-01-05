from .. import records as R, Symbol as S
from . import formatting as FMT


#TODO - define API for row types and add optional runtime check


class Sequence_Based_Row:
	@staticmethod
	def add_row(table, positional, named):
		if named:
			raise NotImplementedError()	#TODO

		assert len(positional) == len(table.columns)

		table.data.append(positional)

	@staticmethod
	def iter_columns(table):
		yield from enumerate(table.columns)


	@staticmethod
	def get_column_name(table, index):
		return table.columns[index]

	@staticmethod
	def iter_row(table, index, row):
		for column_index, column in enumerate(table.columns):
			yield column_index, row[column_index]

	@staticmethod
	def get_row(table, row_index):
		return table.data[row_index]

	@staticmethod
	def resolve_columns(table, columns):
		def rc(col):
			match col:
				case str():
					return table.columns.index(col)
				case int():
					return col

				case symbol if symbol is S.Table.Row_Index:
					return col

			raise TypeError(col)

		return tuple(map(rc, columns))


class Dict_Based_Row:
	@staticmethod
	def reorder_rows(table, new_order):
		new_data = tuple(table.data[index] for index in new_order)
		table.data.clear()
		table.data.extend(new_data)

	@staticmethod
	def add_columns(table, positional, named):
		assert not named #Not supported
		for column in positional:
			if column not in table.columns:
				table.columns.append(column)

	@staticmethod
	def add_row(table, positional, named):
		column_iterator = iter(tuple(table.columns))
		row = dict()
		for value in positional:
			column = next(column_iterator)
			row[column] = value

		for column, value in named.items():
			row[column] = value

		table.add_columns(*row)
		table.data.append(row)

	@staticmethod
	def get_sort_key(table, row_index, column_indices):
		def resolve_key(column_index):
			if column_index is S.Table.Row_Index:
				return row_index
			else:
				return table.data[row_index][column_index]	#TODO: We are currently just sorting it based on raw data but this could be problematic with things we can't compare

		return tuple(map(resolve_key, column_indices))

	@staticmethod
	def get_cell(table, row_index, column_index):
		raise NotImplementedError()

	@staticmethod
	def iter_row(table, index, row):
		for column_index, column in enumerate(table.columns):
			yield column_index, row[column]

	@staticmethod
	def get_column_name(table, index):
		return table.columns[index]

	@staticmethod
	def resolve_columns(table, columns):
		column_names = table.columns
		def rc(col):
			match col:
				case str():
					return col
				case int():
					return column_names[col]

				case symbol if symbol is S.Table.Row_Index:
					return col

			raise TypeError(col)

		return tuple(map(rc, columns))

	@staticmethod
	def iter_columns(table):
		yield from enumerate(table.columns)

class Table_Settings(R.Record):
	all: R.Field() = None
	by_column: R.Field(factory=dict)
	by_row: R.Field(factory=dict)
	by_cell: R.Field(factory=dict)

	def lookup(self, table, row, column):
		return self.by_cell.get((row, column)) or self.by_row.get(row) or self.by_column.get(column) or self.all


class Column_Settings(R.Record):
	all: R.Field() = None
	by_column: R.Field(factory=dict)

	def lookup(self, table, column):
		return self.by_column.get(column) or self.all



class String_Formatter(R.Record):
	table: R.Field()

	def get_length(self, data):
		return len(self.format(data))

	def format(self, data):
		return str(data)


class Function_Formatter(R.Record):
	table: R.Field()
	function: R.Field()

	def get_length(self, data):
		return len(self.format(data))

	def format(self, data):
		return self.function(data)


class Abstract_Table(R.Record):
	columns: R.Field(factory=list)
	cell_formatter: R.Field(factory='_init_default_cell_formatter')
	column_formatter: R.Field(factory='_init_default_column_formatter')
	data: R.Field(factory=list)
	row_type: R.Field() = None
	table_formatter: R.Field(factory=FMT.Simple_Terminal_Formatter)

	def set_column_format(self, column, formatter):
		[column_index] = self.row_type.resolve_columns(self, (column,))
		self.cell_formatter.by_column[column_index] = formatter

	def __len__(self):
		return len(self.data)

	def _init_default_column_formatter(self):
		return Column_Settings(String_Formatter(self))

	def _init_default_cell_formatter(self):
		return Table_Settings(String_Formatter(self))

	def add_columns(__self, *positional, **named):	#We use __self to give more namespace to **named
		__self.row_type.add_columns(__self, positional, named)

	def add_row(__self, *positional, **named):	#We use __self to give more namespace to **named
		__self.row_type.add_row(__self, positional, named)

	def lookup_cell_formatter(self, row_index, column_index):
		return self.cell_formatter.lookup(self, row_index, column_index)

	def lookup_column_formatter(self, column_index):
		return self.column_formatter.lookup(self, column_index)

	def get_column_name(self, column_index):
		return self.row_type.get_column_name(self, column_index)

	def iter_columns(self):
		return self.row_type.iter_columns(self)

	def __iter__(self):
		for index, row in enumerate(self.data):
			yield index, self.row_type.iter_row(self, index, row)

	def format_row_by_index(self, row_index):
		return tuple(self.lookup_cell_formatter(row_index, col_index).format(cell_data) for col_index, cell_data in self.get_row_iter(row_index))

	def format_row(self, index_and_row_iter):
		[index, row_iter] = index_and_row_iter
		return tuple(self.lookup_cell_formatter(index, col_index).format(cell_data) for col_index, cell_data in row_iter)

	def get_row_iter(self, row_index):
		return self.row_type.iter_row(self, row_index, self.row_type.get_row(self, row_index))

	def format(self):
		return self.table_formatter.format(self)

	def resolve_columns(self, *columns):
		return self.row_type.resolve_columns(self, columns)

	def iter_row_indices(self):
		for row_index, row_iterator in self:
			yield row_index

	def sort_by(self, *key_list):
		column_indices = self.resolve_columns(*key_list)
		self.row_type.reorder_rows(self, sorted(self.iter_row_indices(), key=lambda row_index: self.row_type.get_sort_key(self, row_index, column_indices)))


#TODO - rename and reorder abstract and concrete
class Basic_Dict_Table(Abstract_Table):
	row_type: R.Field() = Dict_Based_Row

class Basic_Sequence_Table(Abstract_Table):
	row_type: R.Field() = Sequence_Based_Row


# bt = Basic_Table(Dict_Based_Row)
# bt.add_row(stuff=123, things='hello')
# bt.add_row(456, 'world')
# bt.add_row(789, 'and stuff')

# bt.sort_by('things')
# print(bt.format())
