from . import records as R

class Switchable_Iterator(R.Record):
	source: R.Field()

	def __iter__(self):
		while True:
			try:
				yield next(self.source)
			except StopIteration:
				return
