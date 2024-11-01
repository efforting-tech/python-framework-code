MISS = object()	#TODO - localsymbol

def sliding_slice(sequence, size):
	for index in range(len(sequence) - size + 1):
		yield sequence[index:index+size]

def padded_sliding_slice(sequence, size, pad=None, skip_left=None, skip_right=None, skip=0):

	#sequence = 'ABC', size = 3, skip = 0
	# --- --A -AB ABC BC- C-- ---

	#sequence = 'ABC', size = 3, skip = 1
	# --A -AB ABC BC- C--

	if skip_left is None:
		skip_left = skip

	if skip_right is None:
		skip_right = skip

	pad_left = size - skip_left
	pad_right = size - skip_right

	new_sequence = (pad,) * pad_left + tuple(sequence) + (pad,) * pad_right

	yield from sliding_slice(new_sequence, size)



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

def take_while_consequtive(predicate, source):
	iterator = iter(source)
	for i in iterator:
		if predicate(i):
			yield i
			yield from take_while(predicate, iterator)
			break

