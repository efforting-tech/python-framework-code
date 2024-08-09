from ..record.base.public import Structure
from ..record import member as M
from .. import symbol, ABC

#TODO - Move actions?
@ABC.Action
class Call_Comparator_Function(Structure):
	function = M.positional()

@ABC.Action
class Call_Processing_Function(Structure):
	function = M.positional()

@ABC.Action
class Call_Text_Tree_Processing_Function(Structure):
	function = M.positional()


class Rule(Structure):
	condition = M.positional(None)
	action = M.positional(None)

class LUT_Rule(Structure):
	value = M.positional(None)
	action = M.positional(None)


class Rule_Set(Structure):
	rules = M.positional(factory=list, repr=False)
	fallback = M.positional(None)

	def __iter__(self):
		if isinstance(self.rules, (tuple, list)):
			yield from self.rules
		elif isinstance(self.rules, dict):
			yield from self.rules.values()
		else:
			raise NotImplementedError()	#TODO - is this the correct one? We want to indicate that the descendent didn't implement the proper specific method

	def add_conditional_action(self, condition=None, action=None):
		self.rules.append(Rule(condition, action))

class LUT_Rule_Set(Structure):
	rules = M.positional(factory=dict, repr=False)
	default_action = M.positional(None)
	fallback = M.positional(None)	#TODO - support??


	def map_action(self, value=None, action=None):
		if value is symbol.action.default:
			self.default_action = action
		else:
			self.rules[value] = LUT_Rule(value, action)


	def lookup_action(self, value, default=symbol.action.raise_exception):
		MISS = object()	#TODO - local symbol
		pending = self.rules.get(value, MISS)

		if pending is MISS:
			return self.default_action or default
			#TODO - support fallback??

		if pending is symbol.action.raise_exception:
			raise Exception(value)	#TODO - proper exception
		elif isinstance(pending, LUT_Rule):
			return pending.action
		else:
			return self.default_action or default


class Processor_State(Structure):
	processor = M.positional()
	captures = M.positional(factory=dict)
	capture_meta = M.positional(factory=dict)
	context = M.positional(None)

	#TODO - other API - should we also split them up depending on processor/comparator?
	def compare_items(self, expected, subject):
		return type(self.processor).compare_items(self, expected, subject)

	def store_capture(self, value, name):
		self.captures[name] = value

	def wrap_capture(self, name, wrapper):
		self.captures[name] = wrapper(self.captures[name])

	def process_item(self, item):
		return type(self.processor).process_item(self, item)

	#TODO - maybe we should support default-values to also be factories, if we do this we should make sure the entire project does it like so
	def get_capture(self, name, default=None):
		return self.captures.get(name, default)

	def update_captured_flag(self, name, flag, value):
		if (flag_set := self.captures.get(name)) is None:
			flag_set = self.captures[name] = set()

		if value:	#TODO - should we have special update symbols instead such as set, clear, toggle and such?
			flag_set.add(flag)
		else:
			flag_set.discard(flag)


	#TODO - use some copy protocol?
	def with_processor(self, processor):
		return Processor_State(processor, self.captures, self.capture_meta)

	def __repr__(self):
		return f'{type(self).__qualname__}({self.processor!r})'

	def __getattr__(self, name):
		return getattr(self.processor, name)

@ABC.Decorator
class Pending_LUT_Compare_Function(Structure):
	owner = M.positional()
	action = M.positional()

	def __call__(self, function):
		self.owner.rules.map_action(self.action, Call_Comparator_Function(function))
		return function

@ABC.Decorator
class Pending_LUT_Process_Function(Structure):
	owner = M.positional()
	action = M.positional()

	def __call__(self, function):
		self.owner.rules.map_action(self.action, Call_Processing_Function(function))
		return function

