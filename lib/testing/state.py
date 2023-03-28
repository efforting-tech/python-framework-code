from collections import deque

original_builtins = None
directory = dict()
class_stack = deque()
test_stack = deque()