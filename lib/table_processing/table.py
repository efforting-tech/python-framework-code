from .. import rudimentary_type_system as RTS
from ..rudimentary_type_system.bases import public_base
from ..symbols import register_symbol
from ..rudimentary_type_system.features import method_with_specified_settings, classmethod_with_specified_settings
from ..string_utils import expand_tabs_and_return_line_iterator, remove_blank_lines
from ..iteration_utils import sliding_slice

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
	strip_raster_cells = RTS.setting(True)
	line_comment_pattern = RTS.setting(None)
	configured_columns = RTS.setting(None)
	processing_mode = RTS.setting(PROCESSING.ROW_BY_ROW)
	ditto_columns = RTS.setting(())
	ditto_mark = RTS.setting('〃')
	row_instance = RTS.setting(lambda **x: x.values())
	column_processors = RTS.setting(factory=dict)
	process_columns = RTS.setting(ALL)
	strict_columns = RTS.setting(False)



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
		return self.iter_process.call_with_config(config, process_columns=columns, strict_columns=True)

	@method_with_specified_settings(RTS.SELF)
	def iter_process(self, *, config):	#TODO this must be renamed to correspond to the processing API family

		if config.process_columns is ALL:
			process_columns = self.columns
		else:
			process_columns = config.process_columns

		if config.strict_columns:
			assert len(set(self.columns) & set(process_columns)) == len(set(self.columns)), f'Table has unexpected column configuration. Has columns {self.columns}, expected: {process_columns}'

		column_processors = {column: config.column_processors.get(column, lambda x:x) for column in process_columns}
		column_lut = self.get_column_lut()
		if config.processing_mode is PROCESSING.ROW_BY_ROW:
			if config.ditto_columns is ALL:
				ditto_columns = process_columns
			else:
				ditto_columns = config.ditto_columns

			for column in ditto_columns:
				self.process_column(column, ditto_expansion(config.ditto_mark))

			for row in self.rows:
				yield config.row_instance(**{column: column_processors[column](row[column_lut[column]]) for column in process_columns})

		else:
			raise Exception()



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

