from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol
from ..type_system.features import method_with_specified_settings, classmethod_with_specified_settings
from ..string_utils import expand_tabs_and_return_line_iterator, remove_blank_lines
from ..iteration_utils import sliding_slice

from pathlib import Path

import textwrap, re
from collections import defaultdict

#TODO - representation

#TODO - work more on the configuration system
DEFAULT = register_symbol('internal.default')

class ditto_expansion(public_base):
	ditto_mark = RTS.positional()
	last = RTS.state(None)	#note - if we instead don't initialize we would get an error if ditto expansion is done without previous value. Question is - do we want to readjust the configuration system?

	def __call__(self, value):
		if value != self.ditto_mark:
			self.last = value

		return self.last


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


#TODO enum
class PROCESSING:
	ROW_BY_ROW = register_symbol('internal.table.processing.row_by_row')

ALL = register_symbol('internal.table.columns.all')

#TODO - maybe we should not have column_processor here and instead use a dedicated translator object as we are doing with the improved parsing system
#		one nice thing here would be that the table itself would be a simpler object and then we can add advanced features by hooking in translators and such
#		which might be a bit more elegant
#Note - currently we may not properly handle mutating configuration or columns of table
#Note - this is based from /home/devilholk/Projects/efforting-mvp-2/library/table.py
class table(public_base):
	columns = RTS.optional_factory(tuple)
	rows = RTS.optional_factory(list)

	tab_size = RTS.setting(4)
	min_raster_spacing = RTS.setting(3, description='Minimum spacing required to separate headers in a raster table')
	strip_raster_cells = RTS.setting(True, description='Calls .strip() on cells If set to true when loading raster table.')
	strip_csv_cells = RTS.setting(True, description='Calls .strip() on cells If set to true when loading CSV.')
	strip_columns = RTS.setting(True, description='Calls .strip() on cells in columns. Only matters if strip_raster_cells is set to False.')
	csv_inner_escape_sequences = RTS.setting((('\\\\', '\\'), ('\\,', ',')))
	csv_outer_escape_sequences = RTS.setting((('\\\\', '\\'), ('\\,', ',')))
	csv_quotation = RTS.setting(None)

	csv_column_line = RTS.setting(1)
	csv_delimiter = RTS.setting(',')

	line_comment_pattern = RTS.setting(None)
	configured_columns = RTS.setting(None)
	processing_mode = RTS.setting(PROCESSING.ROW_BY_ROW)
	ditto_columns = RTS.setting(())
	ditto_mark = RTS.setting('〃')
	row_instance = RTS.setting(lambda **x: x.values())
	column_processors = RTS.setting(factory=dict)
	process_columns = RTS.setting(ALL)
	strict_columns = RTS.setting(False)

	multiline_columns = RTS.setting(None)
	multiline_condition = RTS.setting(None)


	def process_column(self, index, filter):
		c_index = self.get_index_by_key(index)

		for index, row in enumerate(self.rows):
			self.rows[index] = (*row[:c_index], filter(row[c_index]), *row[c_index+1:])

	#TODO - cached property
	def get_column_lut(self):
		return {column: index for index, column in enumerate(self.columns)}

	#NOTE - this is a good example for configuration
	@method_with_specified_settings(RTS.SELF)
	def strict_iter(self, *columns, config):
		if columns:
			return self.iter_process.call_with_config(config, process_columns=columns, strict_columns=True)
		else:
			return self.iter_process.call_with_config(config, process_columns=ALL)

	@method_with_specified_settings(RTS.SELF)
	def iter_column(self, column, *, config):
		if isinstance(column, int):
			column = self.columns[column]

		for [cell] in self.iter_process.call_with_config(config, process_columns=(column,)):
			yield cell


	@method_with_specified_settings(RTS.SELF)
	def to_csv_file(self, path, overwrite=False, *, config):
		with Path(path).open('w' if overwrite else 'x') as outfile:
			print(self.csv_join_row.call_with_config(config, self.columns), file=outfile)
			for row in self.rows:
				print(self.csv_join_row.call_with_config(config, row), file=outfile)


	@method_with_specified_settings(RTS.SELF)
	def get_row(self, index, *, config):
		#BUG - we are currently passing columns as a dict which is wrong since columns could have conflicting names, or no names for anonymous columns

		if config.process_columns is ALL:
			process_columns = self.columns
		else:
			process_columns = config.process_columns

		if config.strict_columns:
			assert len(set(self.columns) & set(process_columns)) == len(set(self.columns)), f'Table has unexpected column configuration. Has columns {self.columns}, expected: {process_columns}'

		column_processors = {column: config.column_processors.get(column, lambda x:x) for column in process_columns}
		column_lut = self.get_column_lut()

		multiline_condition = config.multiline_condition
		if multiline_columns := config.multiline_columns:
			multiline_columns = tuple(column_lut.get(c, c) for c in multiline_columns)

		waterfall = multiline_condition and multiline_columns
		row_instance = config.row_instance

		if config.processing_mode is PROCESSING.ROW_BY_ROW:
			if config.ditto_columns is ALL:
				ditto_columns = process_columns
			else:
				ditto_columns = config.ditto_columns

			local_column_processors = {k: ditto_expansion(config.ditto_mark) for k in ditto_columns}
			def process_row_dict(d):
				result = dict()
				for column, cell in d.items():
					if lcp := local_column_processors.get(column):
						cell = lcp(cell)
					result[column] = cell

				return row_instance(**result)

			row = self.rows[index]
			return process_row_dict({column: column_processors[column](row[column_lut[column]]) for column in process_columns})

		else:
			raise Exception()


	@method_with_specified_settings(RTS.SELF)
	def iter_process(self, *, config):	#TODO this must be renamed to correspond to the processing API family

		#BUG - we are currently passing columns as a dict which is wrong since columns could have conflicting names, or no names for anonymous columns

		if config.process_columns is ALL:
			process_columns = self.columns
		else:
			process_columns = config.process_columns

		if config.strict_columns:
			assert len(set(self.columns) & set(process_columns)) == len(set(self.columns)), f'Table has unexpected column configuration. Has columns {self.columns}, expected: {process_columns}'

		column_processors = {column: config.column_processors.get(column, lambda x:x) for column in process_columns}
		column_lut = self.get_column_lut()

		multiline_condition = config.multiline_condition
		if multiline_columns := config.multiline_columns:
			multiline_columns = tuple(column_lut.get(c, c) for c in multiline_columns)

		waterfall = multiline_condition and multiline_columns
		row_instance = config.row_instance

		if config.processing_mode is PROCESSING.ROW_BY_ROW:
			if config.ditto_columns is ALL:
				ditto_columns = process_columns
			else:
				ditto_columns = config.ditto_columns

			local_column_processors = {k: ditto_expansion(config.ditto_mark) for k in ditto_columns}
			def process_row_dict(d):
				result = dict()
				for column, cell in d.items():
					if lcp := local_column_processors.get(column):
						cell = lcp(cell)
					result[column] = cell

				return row_instance(**result)

			if waterfall:
				pending = None

				for row in self.rows:
					processed_row = [column_processors[column](row[column_lut[column]]) for column in process_columns]

					if multiline_condition.check_table_row(column_lut, processed_row):
						if pending:
							for col in multiline_columns:
								pending[col] += f'\n{processed_row[col]}'
						else:
							raise Exception('Pending multiline data before multiline start')
					else:
						if pending:
							yield process_row_dict(dict(zip(process_columns, pending or processed_row)))
							#yield row_instance(**dict(zip(process_columns, pending or processed_row)))
						pending = processed_row

				if pending:	#Catch tail
					#yield row_instance(**dict(zip(process_columns, pending or processed_row)))
					yield process_row_dict(dict(zip(process_columns, pending or processed_row)))

			else:
				#for column in ditto_columns:
					#self.process_column(column, ditto_expansion(config.ditto_mark))

				for row in self.rows:
					#yield row_instance(**{column: column_processors[column](row[column_lut[column]]) for column in process_columns})
					yield process_row_dict({column: column_processors[column](row[column_lut[column]]) for column in process_columns})

		else:
			raise Exception()


	@method_with_specified_settings(RTS.SELF)
	def csv_join_row(self, row, *, config):

		from ..text_processing.tokenization import tokenizer, yield_matched_text, yield_value, token_match
		from ..text_processing.re_tokenization import literal_re_pattern#, SKIP
		#from ..symbols import register_symbol

		if config.csv_quotation:
			qin, qout = config.csv_quotation

			inner_tokenizer = tokenizer()
			inner_tokenizer.default_action = yield_matched_text()

			def join_inner_pieces(p):
				result = str()

				for i in p:
					match i:
						case token_match():
							result += i.value

				return result

			if config.csv_inner_escape_sequences:
				for escape_from, escape_to in config.csv_inner_escape_sequences:
					inner_tokenizer.rules.append((literal_re_pattern(escape_to), yield_value(escape_from)))

			return config.csv_delimiter.join(f'{qin}{join_inner_pieces(inner_tokenizer.tokenize(item))}{qout}' for item in row)

		else:
			raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature



	#TODO - potential huge speedup is to reuse the state once we set it up, we should have a way to give multiple lines
	@method_with_specified_settings(RTS.SELF)
	def csv_split_line(cls, line, allow_empty=False, *, config):

		from ..text_processing.tokenization import tokenizer, enter_tokenizer, yield_value, leave_tokenizer, yield_matched_text, token_match
		from ..text_processing.re_tokenization import literal_re_pattern, SKIP
		from ..symbols import register_symbol
		DELIMITER = register_symbol('internal.delimiter')	#TODO - harmonize
		outer_tokenizer = tokenizer()
		outer_tokenizer.default_action = yield_matched_text()

		if config.csv_quotation:
			inner_tokenizer = tokenizer()
			inner_tokenizer.default_action = yield_matched_text()

			def join_inner_pieces(p):
				result = str()

				for i in p:
					match i:
						case token_match():
							result += i.value

				return result

			qin, qout = config.csv_quotation
			outer_tokenizer.rules.append((literal_re_pattern(qin), enter_tokenizer(inner_tokenizer, post_filter=join_inner_pieces)))

			if config.csv_inner_escape_sequences:
				for escape_from, escape_to in config.csv_inner_escape_sequences:
					outer_tokenizer.rules.append((literal_re_pattern(escape_from), yield_value(escape_to)))

			inner_tokenizer.rules.append((literal_re_pattern(qout), leave_tokenizer()))


		if config.csv_outer_escape_sequences:
			for escape_from, escape_to in config.csv_outer_escape_sequences:
				outer_tokenizer.rules.append((literal_re_pattern(escape_from), yield_value(escape_to)))

		outer_tokenizer.rules.append((literal_re_pattern(config.csv_delimiter), yield_value(DELIMITER)))
		outer_tokenizer.rules.append((re.compile('\s+'), SKIP))


		pending_column = str()
		result = list()
		for c in outer_tokenizer.tokenize(line):
			match c:
				case token_match(value=str()):
					pending_column += c.value

				case token_match() if c.value is DELIMITER:
					assert allow_empty or pending_column
					result.append(pending_column)
					pending_column = str()


				case _ as unhandled:
					raise Exception(f'The value {unhandled!r} could not be handled')


		if pending_column:
			result.append(pending_column)


		return result


	@method_with_specified_settings(RTS.SELF)
	def from_csv_file(cls, path, *, config):

		if config.strip_csv_cells:
			filter_cells = str.strip
		else:
			filter_cells = None

		with Path(path).open('r') as infile:
			pending_rows = tuple(r.rstrip('\r\n') for r in infile)



		if defined_columns := config.configured_columns:
			raise NotImplementedError("This feature is not implemented yet")	#TODO - implement feature
		else:
			columns = cls.csv_split_line.call_with_config(config, pending_rows[config.csv_column_line - 1])

		result = cls(columns)

		for line in pending_rows[config.csv_column_line:]:
			result.append_row(*cls.csv_split_line.call_with_config(config, line, True))

		return result


	@method_with_specified_settings(RTS.SELF)
	def from_raster(cls, text, *, config):
		if config.strip_raster_cells:
			filter_cells = str.strip
		else:
			filter_cells = None

		pending_rows = list()
		lines_to_check = expand_tabs_and_return_line_iterator(textwrap.dedent(text), config.tab_size)

		#TODO make generic function for stripping comments and other text preparation we use here
		if config.line_comment_pattern:
			lcp = re.compile(config.line_comment_pattern)	#TODO - call generic regex resolver

			def check_lines_for_comments(lines_to_check):

				for line in lines_to_check:
					if lcp_match := lcp.search(line):
						yield line[:lcp_match.span()[0]]
					else:
						yield line
			pending_lines = tuple(remove_blank_lines(check_lines_for_comments(lines_to_check)))
		else:
			pending_lines = tuple(remove_blank_lines(lines_to_check))


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

		return cls(defined_columns, pending_rows, **config._target)


	def get_index_by_key(self, key):
		if isinstance(key, int):
			return key
		else:
			return self.get_column_lut()[key]

	def append_row(self, *cells):
		self.rows.append(cells)

	#Todo - maybe add more granularity for auto extension, maybe even config system
	def set_cell(self, row, column, value, auto_extend=False):
		row_count = len(self.rows)
		col_count = len(self.columns)
		last_row = row_count - 1
		last_col = col_count - 1

		if auto_extend:

			if (cols_to_insert := column - last_col) > 0:
				self.columns.extend((f'column_{f}' for f in range(col_count+1, col_count+cols_to_insert+1)))
				col_count = len(self.columns)

			if (rows_to_insert := row - last_row) > 0:
				blank_row = [''] * col_count
				self.rows.extend([blank_row] * rows_to_insert)

		elif row >= row_count or column >= col_count:
			raise Exception('Outside of table')

		self.rows[row][column] = value


	def __repr__(self):
		return f'{self.__class__.__qualname__}({len(self.rows)} rows, {len(self.columns)} columns)'




#Experiment in table translation

SAME_NAME = register_symbol('internal.table.translation.same_name')
USE_TYPE = register_symbol('internal.table.translation.use_type')

class table_translation_source_field(public_base):
	#TODO - we may later add features for per type and such but for now we are starting simple
	field = RTS.positional(default=SAME_NAME)
	type = RTS.positional(default=str)
	#condition = RTS.positional(default=None)
	filter = RTS.positional(default=USE_TYPE)


	def get_field_name(self, target_name):
		if self.field is SAME_NAME:
			return target_name
		else:
			return self.field

	def translate_value(self, value):
		if self.filter is USE_TYPE:
			return self.type(value)
		else:
			return self.filter(value)



class table_translation_config(public_base):
	#TODO - we may later add features for per item filtering, per item target_type and such but for now we are starting simple
	target_type = RTS.positional(field_type=RTS.SETTING)
	translations = RTS.positional(field_type=RTS.SETTING)
	post_processor = RTS.setting(tuple)

	@method_with_specified_settings(RTS.SELF)
	def get_source_fields(self, *, translation_config):
		result = defaultdict(list)
		for target_name, source in translation_config.translations.items():
			result[source.get_field_name(target_name)].append(source)
		return result

	@method_with_specified_settings(RTS.SELF, table)
	def process_table_iteratively(self, table_reference, *, translation_config, table_config):

		columns = self.get_source_fields.call_with_config(translation_config).keys()
		for row in table_reference.strict_iter.call_with_config(table_config, *columns, row_instance=dict):

			target_data = dict()
			for target_name, source in self.translations.items():
				source_field_name = source.get_field_name(target_name)
				cell_value = row[source_field_name]
				target_data[target_name] = source.translate_value(cell_value)

			yield translation_config.target_type(**target_data)

	@method_with_specified_settings(RTS.SELF, table)
	def process_table(self, table_reference, *, translation_config, table_config):
		return translation_config.post_processor(self.process_table_iteratively.call_with_config(translation_config, table_config, table_reference))

