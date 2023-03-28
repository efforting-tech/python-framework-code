
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

