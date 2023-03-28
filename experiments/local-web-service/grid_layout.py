from efforting.mvp4.presets.text_processing import *


class CL:
	layout_token = register_symbol('layout.token')
	number = layout_token()
	separator = layout_token()

layout_tokenizer = tokenizer('layout_tokenizer',
	(re.compile(r'\d+'),				yield_matched_text(CL.number)),
	(re.compile(r'[Xx×*]|\s+by\s+'),	yield_classification(CL.separator)),
	(re.compile(r'\s+'),				SKIP),
)


def create_grid_from_string(cls, definition):
	#TODO - utilize pattern matcher after tokenizer so we don't have to manualy do it here

	last = None
	sub_grids = list()

	for token in layout_tokenizer.tokenize(definition):
		if token.classification is CL.number:
			if last is None:
				last = int(token.match)
			else:
				sub_grids.append(cls(last, int(token.match)))
				last = None

		elif token.classification is CL.separator:
			assert last is not None
		else:
			raise Exception()

	match sub_grids:
		case [grid]:
			return grid
		case [grid, *_]:
			return cls(len(sub_grids), 1)(*sub_grids)  # subgrid_layout(len(sub_grids), 1, None, sub_grids)


	raise Exception()


