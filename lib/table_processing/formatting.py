from .. import type_system as RTS
from ..type_system.bases import public_base

#TODO - be better ablet o handle None and the like in data

class standard_justification:
	'Has one space padding'
	left = 		lambda w: f' {{:<{w}}} '
	right = 	lambda w: f' {{:>{w}}} '
	center = 	lambda w: f' {{:^{w}}} '

class tight_justification:
	'No padding'
	left = 		lambda w: f'{{:<{w}}}'
	right = 	lambda w: f'{{:>{w}}}'
	center = 	lambda w: f'{{:^{w}}}'


#NOTE - there is a problem here with some characters wider than a single one
#		One character that comes to mind is \N{DITTO MARK} (〃)
#		Even wors is that this might be system specific or even application specific
#		We should investigate this a bit at some point but for now we leave formatting without any way
#		to measure certain characters with different width.
#		On the flipside we may have characters that are not printable and hence do not contribute to the width


def get_column_width(tbl, column, include_captions=True):
	column_index = tbl.get_index_by_key(column)
	column_name = tbl.columns[column_index]

	def iter_column(*positional):
		for item in tbl.iter_column(*positional):
			yield str(item)

	if include_captions and column_name:
		#note: we convert this to a tuple in order to include both the column_name and the rows otherwise this will fail if we have an empty table
		seq = (*(len(i) for i in iter_column(column_index)), len(column_name))
	else:
		seq = tuple(len(i) for i in iter_column(column_index))

	if seq:
		return max(seq)	#TODO - check if max has an argument that defaults to 0 in an empty sequence rather than throwing an error
	else:
		return 0


class row_format(public_base):
	left = RTS.positional()
	middle = RTS.positional()
	right = RTS.positional()
	cell_format	 = RTS.positional()
	measure_column_width = RTS.field(default=get_column_width)

	def __call__(self, tbl):
		result = ''

		column_count = len(tbl.columns)
		last_column = column_count - 1
		for c in range(column_count):
			if isinstance(self.cell_format, tuple):
				cell_format = self.cell_format[c]
			else:
				cell_format = self.cell_format

			if c == 0:
				result += self.left

			w = self.measure_column_width(tbl, c)
			result += cell_format(w)

			if c == last_column:
				result += self.right
			else:
				result += self.middle

		return result

class table_format(public_base):
	#Format factories
	top_formatter = RTS.field(default=None)
	head_formatter = RTS.field(default=None)
	neck_formatter = RTS.field(default=None)
	body_formatter = RTS.field(default=None)
	bottom_formatter = RTS.field(default=None)
	no_columns_top_formatter = RTS.field(default=None)

	#Preformatted
	top = RTS.field(default=None)
	head = RTS.field(default=None)
	neck = RTS.field(default=None)
	body = RTS.field(default=None)
	bottom = RTS.field(default=None)
	no_columns_top = RTS.field(default=None)

	_format_fields = 'top head neck body bottom no_columns_top'.split()

	#BUG we are not correcting for cell sizes differing after format

	def format(self, tbl):

		has_columns = any(map(bool, tbl.columns))
		columns = tuple(t or '' for t in tbl.columns)

		# column_processors = {}
		# if filter_table:
		# 	column_processors = dict.fromkeys(tbl.columns, filter_table)

		def _get_format(f):
			pre_formatted = getattr(self, f)
			if pre_formatted is not None:
				return pre_formatted

			factory = getattr(self, f'{f}_formatter')
			if factory is not None:
				return factory(tbl)

		top, head_formatter, neck, body_formatter, bottom, no_columns_top = (_get_format(c) for c in self._format_fields)

		result = list()
		if has_columns:
			if top:
				result.append(top)

			if head_formatter:
				result.append(head_formatter.format(*columns))

			if neck:
				result.append(neck)

		else:
			if no_columns_top:
				result.append(no_columns_top)


		if body_formatter:
			#for row in tbl.iter_process(column_processors=column_processors):
			for row in tbl.iter_process():
				result.append(body_formatter.format(*row))

		if bottom:
			result.append(bottom)

		return '\n'.join(result)


SJ, TJ = standard_justification, tight_justification

efforting_table = table_format(
	head_formatter = 	row_format('', '   ', '', TJ.left),
	neck_formatter = 	row_format('', '   ', '', lambda w: '-' * w),
	body_formatter = 	row_format('', '   ', '', TJ.left),
)

zim_table = table_format(
	head_formatter = 	row_format('|', '|', '|', SJ.left),
	neck_formatter = 	row_format('|', '|', '|', lambda w: ':' + '-' * max((w + 1), 1)),
	body_formatter = 	row_format('|', '|', '|', SJ.left),
)

terminal_table = table_format(
	no_columns_top_formatter = 	row_format('┍', '┯', '┑', lambda w: '━' * (w + 2)),
	top_formatter = 			row_format('┏', '┳', '┓', lambda w: '━' * (w + 2)),
	head_formatter = 			row_format('┃', '┃', '┃', SJ.center),
	neck_formatter = 			row_format('┡', '╇', '┩', lambda w: '━' * (w + 2)),
	body_formatter = 			row_format('│', '│', '│', SJ.left),
	bottom_formatter = 			row_format('╰', '┴', '╯', lambda w: '─' * (w + 2)),
)
