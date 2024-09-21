from . import record as R
import re
from .iteration import sliding_slice

class Default_Raster_Table_Config:
	strip_raster_cells = True
	strip_columns = True
	line_comment_pattern = r'#.*'
	configured_columns = None
	min_raster_spacing = 3


#TODO - move to string utils
def remove_blank_lines(line_generator):
	for l in line_generator:
		if l.strip():
			yield l



def iter_columns_from_line(line, min_spacing):
	last_column = None
	pending = True
	spaces = 0

	for i, c in enumerate(line):
		if pending and c != ' ':
			if last_column is None or spaces >= min_spacing:
				yield i

			last_column = i
			pending = False
			spaces = 0
		elif c == ' ':
			spaces += 1
			pending = True


class Interface:

	class Core(R.Record):
		instance: R.Field()
		start_index: R.Field() = 0

		def __get__(self, instance, owner):
			return type(self)(instance)

	class Column(Core):
		def __getitem__(self, address):
			#TODO - manage slices and regions and stuff
			#TODO - should probably use a specific interface rather than private access

			col_index = self.start_index

			match address:
				case int() as col:
					return tuple(r[col - col_index] for r in self.instance._rows)

				case unhandled:
					raise Exception(address)

	class Row(Core):
		def __getitem__(self, address):
			#TODO - manage slices and regions and stuff
			#TODO - should probably use a specific interface rather than private access

			row_index = self.start_index

			match address:
				case int() as row:
					return tuple(self.instance._rows[row - row_index])

				case unhandled:
					raise Exception(address)

	class Cell(Core):
		start_index: R.Field() = 0, 0

		def __getitem__(self, address):
			#TODO - manage slices and regions and stuff
			#TODO - should probably use a specific interface rather than private access

			row_index, col_index = self.start_index

			match address:
				case [int() as row, int() as col]:
					return self.instance._rows[row - row_index][col - col_index]

				#case [slice() as row, slice() as col]:
				#	... Table_View?

				case unhandled:
					raise Exception(address)


class Core_Table(R.Record):
	_columns: R.Field(factory=list)
	_rows: R.Field(factory=list)

	#TODO - R.Interface
	column = Interface.Column()
	row = Interface.Row()
	cell = Interface.Cell()



class Raster_Table(Core_Table):
	@classmethod
	def from_line_view(cls, source):
		return cls.from_lines(tuple(line.text for line in source))


	@classmethod
	def from_lines(cls, source, config=Default_Raster_Table_Config):

		if config.strip_raster_cells:
			filter_cells = str.strip
		else:
			filter_cells = None

		pending_rows = list()


		#TODO make generic function for stripping comments and other text preparation we use here
		if config.line_comment_pattern:
			lcp = re.compile(config.line_comment_pattern)	#TODO - call generic regex resolver

			def check_lines_for_comments(lines_to_check):

				for line in lines_to_check:
					if lcp_match := lcp.search(line):
						yield line[:lcp_match.span()[0]]
					else:
						yield line
			pending_lines = tuple(remove_blank_lines(check_lines_for_comments(source)))
		else:
			pending_lines = tuple(remove_blank_lines(source))


		if defined_columns := config.configured_columns:
			raise Exception('Should we really check pending_lines here?')
			if pending_lines:
				columns = tuple(iter_columns_from_line(pending_lines[0], config.min_raster_spacing))
		else:
			if pending_lines:
				columns = tuple(iter_columns_from_line(pending_lines[0], config.min_raster_spacing))

				assert len(set(pending_lines[1])) in (0, 1, 2)		#0 = blank lines, 1 = only one symbol, 2 = only two symbols (like dash and space)

				if filter_cells:
					defined_columns = tuple(filter_cells(pending_lines[0][c:nc]) for c, nc in sliding_slice((*columns, None), 2))
				else:
					defined_columns = tuple(pending_lines[0][c:nc] for c, nc in sliding_slice((*columns, None), 2))

				if config.strip_columns and not config.strip_raster_cells:
					defined_columns = tuple(c.strip() for c in defined_columns)


				pending_lines = pending_lines[2:]

		if pending_lines:
			for l in pending_lines:
				if filter_cells:
					cells = tuple(filter_cells(l[c:nc]) for c, nc in sliding_slice((*columns, None), 2))
				else:
					cells = tuple(l[c:nc] for c, nc in sliding_slice((*columns, None), 2))

				pending_rows.append(cells)

		return cls(defined_columns, pending_rows)

