from collections import deque

RAISE_EXCEPTION = object()	#TODO - should be a symbol
EMPTY = object()

class branchable_iterator:
	def __init__(self, source):
		self.source = iter(source)
		self.pending = deque()
		#self.popped_items = 0

	def push(self, item):
		self.pending.appendleft(item)

	def peek(self, default=RAISE_EXCEPTION):
		try:
			item = self.pop()
			self.push(item)
			return item
		except StopIteration:
			if default is RAISE_EXCEPTION:
				raise
			else:
				return default

	def pop(self, default=RAISE_EXCEPTION):
		if self.pending:
			return self.pending.popleft()
		else:
			#self.popped_items += 1
			try:
				return next(self.source)
			except StopIteration:
				if default is RAISE_EXCEPTION:
					raise
				else:
					return default

	#@property
	#def pending_items(self):
		#return self.popped_items - len(self.pending)

	#This branch is exhausting the supply and there might be use cases for an iterator that does not do that and only keep the buffer between the iterator that popped the most and least items from source
	#But for implementation simplicity right now the exhaustive method is used

	def branch(self):
		pending = tuple(self.pending) + tuple(self.source)
		self.pending.clear()
		result = self.__class__(iter(pending))
		self.pending += pending
		return result

	def fast_forward(self, count):
		for i in range(count):
			self.pop()

	def fast_forward_to(self, child_iterator):
		'fast forward to identity match'
		target = child_iterator.peek()
		while self.peek() is not target:
			self.pop()

		#self.fast_forward(child_iterator.pending_items)
		#print(self.peek(), child_iterator.peek())

	def is_empty(self):
		return self.peek(EMPTY) is EMPTY

	def __iter__(self):
		return self

	__next__ = pop
