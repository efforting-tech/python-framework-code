from efforting.mvp6.record.base.public import Structure
from efforting.mvp6.record import member as M
from efforting.mvp6 import symbol
import time

# code = '''

# def function():
# 	print(G)

# '''

# scope = dict()
# exec(code, scope)
# f = scope['function']

# print(f.__globals__ is scope)	#True

# scope['G'] = 123
# print(f())



class execution_frame(Structure):
	pending_frames = M.positional()
	code = M.positional()
	context = M.positional(None)
	started = M.positional(None)
	stopped = M.positional(None)

	def __enter__(self):
		self.started = time.monotonic()
		self.pending_frames.add(self)
		return self

	def __exit__(self, et, ev, tb):
		self.stopped = time.monotonic()
		self.pending_frames.discard(self)

class execution_tracker(Structure):
	pending = M.positional(factory=set)

	def execute_code_in_context(self, code, context):
		entry = execution_frame(self.pending, code, context)
		return entry

class logging_execution_tracker(execution_tracker):
	log = M.positional(factory=list)

	def execute_code_in_context(self, code, context):
		entry = execution_frame(self.pending, code, context)
		self.log.append(entry)
		return entry

class python_code_execution_interface:
	@staticmethod
	def exec_in_context(context, code, tracker=None):
		if (t := tracker or context.tracker):
			with t.execute_code_in_context(code, context):
				exec(code, context.to_dict(), context.locals)
		else:
			exec(code, context.to_dict(), context.locals)


class context_dict_interface(Structure):
	context = M.positional()

	def __getitem__(self, key):
		return self.context.get(key)	#TODO - handle miss

	def __setitem__(self, key, value):
		self.context.set(key, value)

	def __delitem__(self, key):
		self.context.delete(key)

	def __contains__(self, key):
		return self.context.has_key(key)

	def __iter__(self):
		yield from self.context.strict_iter_members(True)

	def __len__(self):
		return len(self.context.get_set_of_keys())



class context(Structure):
	name = M.positional(None)
	locals = M.positional(factory=dict, repr=False)
	parent = M.positional(None, repr=False)
	tracker = M.positional(None, repr=False)

	def get_set_of_keys(self):
		keys = set()
		for ctx in self.iter_ancestors():
			keys |= set(ctx.locals)

		return keys

	def sub_context(self, locals=None, name=symbol.copy, tracker=symbol.copy):
		if name is symbol.copy:
			name = self.name
		if tracker is symbol.copy:
			tracker = self.tracker

		return type(self)(name, dict() if locals is None else locals, parent=self, tracker=tracker)

	def iter_ancestors(self, reversed=False):
		if reversed:
			yield self
			if self.parent:
				yield from self.parent.iter_ancestors(reversed)
		else:
			if self.parent:
				yield from self.parent.iter_ancestors(reversed)
			yield self

	def iter_members(self):
		for ctx in self.iter_ancestors():
			yield from ctx.locals.items()

	def strict_iter_members(self, reversed=False):
		seen = set()
		for ctx in self.iter_ancestors(reversed):
			for key, value in ctx.locals.items():
				if key not in seen:
					seen.add(key)
					yield (key, value)


	def to_dict(self):
		return dict(self.iter_members())

	def set(self, key, value):
		self.locals[key] = value

	def delete(self, key):
		del self.locals[key]

	def get(self, key, default=None):
		MISS = object()	#TODO - local symbol
		for ctx in self.iter_ancestors(True):
			if (value := ctx.locals.get(key, MISS)) is not MISS:
				return value

		return default

	def has_key(self, key):
		for ctx in self.iter_ancestors(True):
			if key in ctx.locals:
				return True

		return False


r = context('test', dict(stuff=123))
sc = r.sub_context(dict(stuff=456, thing=123))

cdi = context_dict_interface(sc)
#cdi['stuff'] = 'hello'

et = execution_tracker()

r.set('et', et)

code = '''

print(et.pending)

'''

python_code_execution_interface.exec_in_context(sc, code, tracker=et)
#exec('stuff = 5\nprint(stuff)', dict(cdi), cdi.context.locals)


print(sc.locals['stuff'])



#python_code_execution_interface.execute_(sc
