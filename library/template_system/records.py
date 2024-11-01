from ..core import record as R

class MAST:
	class Include(R.Record):
		path: R.Field()

	class Tree(R.Record):
		title: R.Field()
		body: R.Field()

	Well_Known = E('Well_Known',
		'Current_Function',
	)

