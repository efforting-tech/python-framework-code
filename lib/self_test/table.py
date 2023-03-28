from efforting.mvp4.testing import load_testing_framework, unload_testing_framework

load_testing_framework()
# class Test:
# 	pass


from efforting.mvp4.table_processing.table import table

#TODO - proper tests
class basic(Test):
	t = table.from_raster(r'''

		pattern		description					regex
		-------		-----------					-----
		rw			capturing required word		r'(\w+)'
		ow			capturing optional word		r'(\w*)'
		·			optional space				r'\s*'
		stuf		thing						"
	''')

	for pattern, regex in t.iter_process(process_columns=('pattern', 'regex'), ditto_mark='"', ditto_columns=('regex',)):
		print(pattern, regex)

class all(TestGroup, include=(basic,)):
	pass

all.run().present()