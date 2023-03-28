from efforting.mvp4.presets.text_processing import *
from efforting.mvp4 import auto_convert
from efforting.mvp4.abstract_base_classes.interfaces import auto_conversion

#Thoughts - it would be nice if items in list_of automatically had an index

class db_base(public_base):
	pass


class list_of(db_base, auto_conversion):
	element_type = RTS.positional()

	def __call__(self):
		return list_instance(self)

	def convert(self, item):
		return list_instance(self, deque((auto_convert(i, self.element_type) for i in item)))

	def __instancecheck__(self, other):
		return isinstance(other, deque) and all(isinstance(i, self.element_type) for i in other)


class list_instance(db_base):
	type = RTS.positional()
	contents = RTS.factory(deque)
	indices = RTS.factory(dict)

	def append(self, item):
		#TODO type check
		pending_index = len(self.contents)
		self.contents.append(auto_convert(item, self.type.element_type))
		self.indices[item] = pending_index
		#owner_lut.by_owner[self] = item
		#TODO register ownership indices if this is wanted (for making querying the db easier)

	def __iter__(self):
		yield from self.contents


class layout(db_base):

	def format(self):
		if self.owner:
			return self.owner.format()

class grid_reference(db_base):
	grid = RTS.positional()
	row = RTS.positional()
	column = RTS.positional()

	def format(self):
		if gf := self.grid.format():
			return f'{gf}, {self.row+1}:{self.column+1}'
		else:
			return f'{self.row+1}:{self.column+1}'


class subgrid_layout(layout):
	rows = RTS.field()
	columns = RTS.field()
	owner = RTS.field()
	sub_layouts = RTS.field(default=None)


	def count_cells(self):
		cells = 0
		for sl in self.sub_layouts:
			if sl is None:
				cells += 1
			else:
				cells += sl.count_cells()
		return cells

	def iter_slot_indices(self):
		for (row, col), sl in zip(itertools.product(range(self.rows), range(self.columns)), self.sub_layouts):
			gref = grid_reference(self, row, col)

			for sub_ref in sl.iter_slot_indices():
				yield grid_reference(gref, sub_ref.row, sub_ref.column)


class grid_layout(layout):
	rows = RTS.field()
	columns = RTS.field()
	owner = RTS.field()


	class CL:
		layout_token = register_symbol('layout.token')
		number = layout_token()
		separator = layout_token()

	layout_tokenizer = tokenizer('layout_tokenizer',
		(re.compile(r'\d+'),				yield_matched_text(CL.number)),
		(re.compile(r'[Xx×*]|\s+by\s+'),	yield_classification(CL.separator)),
		(re.compile(r'\s+'),				SKIP),
	)

	def iter_slot_indices(self):
		for row, col in itertools.product(range(self.rows), range(self.columns)):
			yield grid_reference(self, row, col)



	def count_cells(self):
		return self.rows * self.columns

	@classmethod
	def from_string(cls, definition):
		#TODO - utilize pattern matcher after tokenizer so we don't have to manualy do it here

		last = None
		sub_grids = list()

		for token in cls.layout_tokenizer.tokenize(definition):
			if token.classification is cls.CL.number:
				if last is None:
					last = int(token.match)
				else:
					sub_grids.append(grid_layout(last, int(token.match), None))
					last = None

			elif token.classification is cls.CL.separator:
				assert last is not None
			else:
				raise Exception()

		match sub_grids:
			case [grid]:
				return grid
			case [grid, *_]:
				sgl = subgrid_layout(len(sub_grids), 1, None, sub_grids)
				#Change owner for sub grids
				for sg in sub_grids:
					sg.owner = sgl

				return sgl


		raise Exception()




class measure(db_base):
	pass


class measure(measure):
	value = RTS.positional()
	unit = RTS.positional()

	def format(self):
		return format_unit_value(self.unit, self.value)

class sku_amount(db_base):
	item = RTS.positional()
	measure = RTS.positional()

	def format(self):
		return f'{self.item.format()} {self.measure.format()}'

class container_cell(db_base):
	index = RTS.positional()
	contents = RTS.factory(list_of(sku_amount))

class container(db_base):
	layout = RTS.positional()
	contents = RTS.positional()


class prefixed_unit(db_base):
	prefix = RTS.positional()
	unit = RTS.positional()

#Note that scaled unit is for real numbers, for natural numbers we use multiples_unit
class scaled_unit(db_base):
	short = RTS.positional()
	unit = RTS.positional()
	scale = RTS.positional()
	long = RTS.field(None)

	def __set_name__(self, target, name):
		self.long = name

class multiples_unit(db_base):
	short = RTS.positional()
	unit = RTS.positional()
	multiple = RTS.positional()
	long = RTS.field(None)

	def __set_name__(self, target, name):
		self.long = name

class si_prefix(db_base):
	short = RTS.positional()
	scale = RTS.positional()
	long = RTS.field(None)

	def __set_name__(self, target, name):
		self.long = name

class SI_PREFIX:
	mega = si_prefix('M', 1e6)
	kilo = si_prefix('k', 1e3)
	deci = si_prefix('d', 1e-1)
	centi = si_prefix('c', 1e-2)
	milli = si_prefix('m', 1e-3)
	micro = si_prefix('µ', 1e-6)


class unit(db_base):	#TODO - maybe generalize with si_prefix
	parent = RTS.field(None)
	short = RTS.field(None)
	long = RTS.field(None)

	def __set_name__(self, target, name):
		self.long = name



class U:

	volume = unit()
	mass = unit()
	count = unit()
	energy = unit()

	joule = unit(energy, 'J')
	liter = unit(volume, 'l')
	gram = unit(mass, 'g')

	dl = prefixed_unit(SI_PREFIX.deci, liter)
	cl = prefixed_unit(SI_PREFIX.centi, liter)
	ml = prefixed_unit(SI_PREFIX.milli, liter)
	micro_l = prefixed_unit(SI_PREFIX.micro, liter)

	kg = prefixed_unit(SI_PREFIX.kilo, gram)
	mg = prefixed_unit(SI_PREFIX.milli, gram)
	micro_g = prefixed_unit(SI_PREFIX.micro, gram)

	ton = scaled_unit('t', kg, 1000)
	kton = prefixed_unit(SI_PREFIX.kilo, ton)

	doz = dozen = multiples_unit('doz', count, 12)	#note order of multiple assignments, last one will be used for long name via __set_name__


def format_unit_value(unit, value, prefix=None):
	if prefix:
		is_multiple = isinstance(prefix.scale, int) and prefix.scale > 1
		p = prefix.short
	else:
		p = ''

	match unit:
		case U.count:
			assert isinstance(value, int)
			assert (not prefix) or is_multiple
			return f'{value} {p}pcs'

		case U.liter:
			return f'{value:0.2f} {p}{unit.short}'

		case prefixed_unit(prefix=prefix, unit=sub_unit):
			return format_unit_value(sub_unit, value, prefix)

		case scaled_unit(short=name):
			return f'{value:0.2f} {p}{name}'

		case multiples_unit(short=name):
			assert isinstance(value, int)	#note this should not be done here
			return f'{value} {p}{name}'

	raise Exception(unit)


class item_definition(db_base):
	name = RTS.positional()

	def format(self):
		return self.name

