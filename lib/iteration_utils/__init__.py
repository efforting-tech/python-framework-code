MISS = object()	#TODO symbol
#TODO - harmonize more from /home/devilholk/Projects/efforting-mvp-2/library/iter_utils.py
def sliding_slice(sequence, size):
	for index in range(len(sequence) - size + 1):
		yield sequence[index:index+size]


def consequtive_slice(sequence, size, strict=True):
	pieces = len(sequence) // size
	if strict:
		assert pieces * size == len(sequence)
	for index in range(pieces):
		yield sequence[index*size : (index+1)*size]


def single_item(collection):
	[item] = collection
	return item


def last(gen):
	item = MISS
	for item in gen:
		pass
	if item is MISS:
		raise Exception()
	return item

def first(gen):
	for item in gen:
		return item
	else:
		raise Exception()

def iter_max_count(iterator, max_count):
	for count, item in enumerate(iterator, 1):
		yield item
		if count == max_count:
			return

def maybe_next(iterator, default=None):
	try:
		return next(iterator)
	except StopIteration:
		return default