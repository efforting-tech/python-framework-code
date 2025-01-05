from .. import records as R

from .formatting import Format_Side_By_Side



class Table_Mismatch_Exception(Exception):
	def __init__(self, expected, tested, row=None):

		info = Format_Side_By_Side(f'Expected table:\n{expected.format()}', f'Tested table:\n{tested.format()}', separator=' '*3)

		if row:
			super().__init__(f'Table mismatch detected on row {row}.\n\n{info}')
		else:
			super().__init__(f'Table mismatch detected.\n\n{info}')
		self.expected = expected
		self.tested = tested

class Table_Unordered_Mismatch_Exception(Exception):
	def __init__(self, expected, tested, key_name=None, row_key=None):

		info = Format_Side_By_Side(f'Expected table:\n{expected.format()}', f'Tested table:\n{tested.format()}', separator=' '*3)

		if key_name is not None:
			cond = f'{key_name!r} = {row_key!r}'
			super().__init__(f'Table mismatch detected where {cond}.\n\n{info}')
		else:
			super().__init__(f'Table mismatch detected.\n\n{info}')
		self.expected = expected
		self.tested = tested

class Abstract_Format_And_Match_Table_Proxy(R.Record):
	expected_table: R.Field()
	tested_table: R.Field()

	def add_row(self, *positional, **named):
		self.tested_table.add_row(*positional, **named)
		self.test()

class Continuous_Format_And_Match_Table_Proxy(Abstract_Format_And_Match_Table_Proxy):
	last_checked_row: R.Field() = 0

	def test(self):
		for row, (expected, tested) in enumerate(zip(self.expected_table, self.tested_table), 1):
			if row > self.last_checked_row:
				expected_value = self.expected_table.format_row(expected)
				tested_value = self.tested_table.format_row(tested)
				if expected_value != tested_value:
					raise Table_Mismatch_Exception(self.expected_table, self.tested_table, row)
				self.last_checked_row = row


#NOTE: The idea for this was to compare states that are created out of order but the problem is that when we combine this with automatic keys we will fail matching
#		this implementation may still have some use cases but not what I had in mind when writing it.
#
class Continuous_Unordered_Format_And_Match_Table_Proxy(Abstract_Format_And_Match_Table_Proxy):
	key: R.Field() = 0

	def test(self):
		[key] = self.expected_table.resolve_columns(self.key)

		tested_rows = (self.tested_table.format_row(tested) for tested in self.tested_table)
		tested_lut = {row[key]:row for row in tested_rows}

		for expected in self.expected_table:
			row = self.expected_table.format_row(expected)
			row_key = row[key]

			if (test_row := tested_lut.get(row_key)) is not None:
				if row != test_row:
					raise Table_Unordered_Mismatch_Exception(self.expected_table, self.tested_table, self.expected_table.columns[key], row_key)

			#row_key = expected[key]


