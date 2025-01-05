from .. import records as R
from itertools import chain

#TODO - support stacking formatters so that we could add thigns for highlighting a line or column later
#		this could either be done by having a formatter chain object we could use
#		or it could be supported by Table_Settings and Column_Setting from the start
#		We should probably add some drysoot to those classes anyway.

#TODO - support SOX/EOX for width testing (this should probably go into a utility module)

class Simple_Terminal_Formatter(R.Record):
	use_middle_divider: R.Field() = False

	def format(self, table):
		# This function was mostly written by ChatGPT 4o by OpenAI

		# Collate header and body to calculate column widths
		column_widths = {}
		headers = {}

		# Determine column widths by considering both headers and body
		for col_index, column in table.iter_columns():
			column_fmt = table.lookup_column_formatter(col_index)
			header = table.get_column_name(col_index)
			headers[col_index] = column_fmt.format(header) if column_fmt else header
			column_widths[col_index] = column_fmt.get_length(headers[col_index]) if column_fmt else len(header)

		for row_index, row_iter in table:
			for col_index, cell_data in row_iter:
				cell_fmt = table.lookup_cell_formatter(row_index, col_index)
				cell_length = cell_fmt.get_length(cell_data)
				column_widths[col_index] = max(column_widths[col_index], cell_length)

		# Box drawing characters
		top_left = "\u250C"
		top_right = "\u2510"
		bottom_left = "\u2514"
		bottom_right = "\u2518"
		horizontal = "\u2500"
		vertical = "\u2502"
		junction_top = "\u252C"
		junction_bottom = "\u2534"
		junction_left = "\u251C"
		junction_right = "\u2524"
		junction_center = "\u253C"

		# Generate horizontal dividers
		def horizontal_divider(left, middle, right):
			parts = [left]
			for col_index, width in sorted(column_widths.items()):
				parts.append(horizontal * (width + 2))  # Add padding
				if col_index < max(column_widths):
					parts.append(middle)
			parts.append(right)
			return "".join(parts)

		top_divider = horizontal_divider(top_left, junction_top, top_right)
		bottom_divider = horizontal_divider(bottom_left, junction_bottom, bottom_right)
		middle_divider = horizontal_divider(junction_left, junction_center, junction_right)

		# Create column headers
		column_headers = []
		for col_index in sorted(column_widths):
			column_headers.append(f" {headers[col_index]:<{column_widths[col_index]}} ")
		header_row = vertical + vertical.join(column_headers) + vertical

		# Format the rows
		rows = []
		for row_index, row_iter in table:
			row_parts = []
			for col_index, cell_data in row_iter:
				cell_fmt = table.lookup_cell_formatter(row_index, col_index)
				formatted_data = cell_fmt.format(cell_data)
				row_parts.append(f" {formatted_data:<{column_widths[col_index]}} ")
			rows.append(vertical + vertical.join(row_parts) + vertical)

		# Combine everything
		formatted_table = [top_divider, header_row, middle_divider]
		for i, row in enumerate(rows):
			formatted_table.append(row)
			if self.use_middle_divider and i < len(rows) - 1:
				formatted_table.append(middle_divider)
		formatted_table.append(bottom_divider)

		return "\n".join(formatted_table)



#TODO - move to iteration utils
def Repeat_Forever(item):
	while True:
		yield item

#TODO - move to generic string formatting
def Format_Side_By_Side(*pieces, separator=' '):
	sizes = tuple(max(len(r) for r in p.splitlines()) for p in pieces)
	line_format = separator.join(f'{{:{s}s}}' for s in sizes)

	result = ''
	for line in zip(*(chain(p.splitlines(), Repeat_Forever('')) for p in pieces)):
		if all(not cell for cell in line):
			break
		result += f'{line_format.format(*line)}\n'

	return result


