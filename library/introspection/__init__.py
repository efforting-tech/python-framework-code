from collections import Counter
import sys

class stack_limit:

	def __init__(self, depth, frame_counter=None):
		self.depth = depth
		if frame_counter is None:
			frame_counter = Counter()

		self.frame_counter = frame_counter


	def __enter__(self):
		calling_frame = sys._getframe(1)
		key = calling_frame.f_code, calling_frame.f_lineno
		count = self.frame_counter[key] = self.frame_counter[key] + 1
		if count > self.depth:
			self.frame_counter[key] = self.frame_counter[key] - 1
			raise RecursionError('max_stack depth exceeded')


	def __exit__(self, et, ev, tb):
		calling_frame = sys._getframe(1)
		key = calling_frame.f_code, calling_frame.f_lineno
		self.frame_counter[key] = self.frame_counter[key] - 1