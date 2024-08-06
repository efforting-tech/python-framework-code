from .record.base.public import Structure
from .record import member as M
from . import symbol
import time

class execution_frame(Structure):
	owner = M.positional()
	code = M.positional()
	context = M.positional(None)
	started = M.positional(None)
	stopped = M.positional(None)

	def __enter__(self):
		self.started = time.monotonic()
		if (ft := self.owner.frame_tracker) is not None:
			ft.push(self)
		return self

	def __exit__(self, et, ev, tb):
		self.stopped = time.monotonic()

		if et and (t := self.owner.exception_tracker):
			t.track_exception(self, et, ev, tb)

		if (ft := self.owner.frame_tracker) is not None:
			ft.pop()


class stack(list):
	def push(self, value):
		self.append(value)

	def pop(self):
		return super().pop(-1)

	@property
	def top(self):
		if self:
			return self[-1]


class execution_tracker(Structure):
	#TODO - this should be split up in specific sub trackers
	exception_tracker = M.positional(symbol.target.instance)	#TODO/BUG - investigate why we get a member.utils.constant here
	frame_tracker = M.positional(factory=stack)

	def execute_code_in_context(self, code, context):
		entry = execution_frame(self, code, context)
		return entry

	def track_exception(self, ef, et, ev, tb):
		try:
			from efforting.mvp6.text.styling.terminal import stylize_and_render_document
			from efforting.mvp6.text.styling import presets
			from efforting.mvp6.document import create_line_listing_document_from_str
			import re
			code_listing = create_line_listing_document_from_str(self.frame_tracker.top.code)
			hl_spans = [(re.compile('.*', re.DOTALL).match(self.frame_tracker.top.code, *code_listing.lines[tb.tb_next.tb_frame.f_lineno - 1].span), 'highlight')]	#TODO - this should be a string utility

			print(stylize_and_render_document(code_listing, presets.fruity, highlight_spans = hl_spans))
		except Exception as e:
			print('EEEE', e)


class logging_execution_tracker(execution_tracker):
	log = M.positional(factory=list)

	def execute_code_in_context(self, code, context):
		entry = execution_frame(self, code, context)
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

	def require(self, key):
		MISS = object()	#TODO - local symbol
		for ctx in self.iter_ancestors(True):
			if (value := ctx.locals.get(key, MISS)) is not MISS:
				return value

		raise Exception(key)

	def has_key(self, key):
		for ctx in self.iter_ancestors(True):
			if key in ctx.locals:
				return True

		return False

