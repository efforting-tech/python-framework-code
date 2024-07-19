#Improved formatting system
import colorsys

#TODO - provide local record/structure system
from efforting.mvp5.lazy_resources import acquire
TS, Public_Base = acquire('TS, TS_pb')


class HSV(Public_Base):
	hue = TS.positional()
	saturation = TS.positional()
	value = TS.positional()

	def to_rgb(self):
		return RGB(*colorsys.hsv_to_rgb(self.hue, self.saturation, self.value))

class RGB(Public_Base):
	red = TS.positional()
	green = TS.positional()
	blue = TS.positional()

	def to_integers(self, bit_depth=8):
		return tuple(int(c * ((1 << bit_depth) - 1)) for c in (self.red, self.green, self.blue))

class Stylized_Span(Public_Base):
	style = TS.positional(default=None)
	text = TS.positional(factory=list)		#Note that text can be strings or sequences of other stylized items

	def setup_list(self):
		match self.text:
			case list():
				pass
			case tuple() as sequence:
				self.text = list(sequence)
			case nothing if nothing is None:
				self.text = []
			case anything:
				self.text = [anything]

	@property
	def last_item(self):
		match self.text:
			case (tuple() | list()) as sequence if len(self.text):
				return self.text[-1]
			case nothing if nothing is None:
				return
			case anything:
				return self.text

	def write_stylized(self, style, text):
		self.setup_list()
		last_item = self.last_item
		if isinstance(last_item, type(self)) and last_item.style == style:
			last_item.write(text)
		else:
			self.text.append(type(self)(style, text))

	def write(self, text):
		self.setup_list()
		if isinstance(text, str) and isinstance(self.last_item, str) :
			self.text[-1] += text
		else:
			self.text.append(text)


class Style(Public_Base):
	name = TS.positional()
	push = TS.positional(factory=list)
	pop = TS.positional(factory=list)

class Style_Manager(Public_Base):
	name = TS.positional(default=None)
	lut = TS.positional(factory=dict)

	def define_style(self, name, push=(), pop=()):
		self.lut[name] = Style(name, push, pop)

	def render_push(self, style):
		match style:
			case Style():
				yield from style.push
			case anything as key:
				yield from self.lut[key].push

	def render_pop(self, style):
		match style:
			case Style():
				yield from style.pop
			case anything as key:
				yield from self.lut[key].pop



class Filter:
	class function(Public_Base):
		function = TS.positional()

		def __call__(self, text):
			return self.function(text)

class Event:
	class push(Public_Base):
		stack = TS.positional()
		value = TS.positional()

	class pop(Public_Base):
		stack = TS.positional()

class State_Heap(Public_Base):
	lut = TS.all_named()

	def get_state(self):
		return {key: stack.value for key, stack in self.lut.items()}

class State_Span(Public_Base):
	state = TS.positional()
	text = TS.positional(default='')

class Filter_Stack(Public_Base):
	name = TS.positional(default=None)
	stack = TS.positional(factory=list)

	@property
	def value(self):
		return tuple(self.stack)

	def push(self, value):
		self.stack.append(value)

	def pop(self):
		self.stack.pop(-1)

class Flag_Stack(Public_Base):
	name = TS.positional(default=None)
	stack = TS.positional(factory=set)

	@property
	def value(self):
		return frozenset(self.stack)

	def push(self, value):
		self.stack.add(value)

	def pop(self):
		self.stack.discard(value)

class State_Stack(Public_Base):
	name = TS.positional(default=None)
	default = TS.positional(default=None)
	stack = TS.positional(factory=list)

	@property
	def value(self):
		if self.stack:
			return self.stack[-1]
		else:
			return self.default

	def push(self, value):
		self.stack.append(value)

	def pop(self):
		self.stack.pop(-1)



def get_style_operations(source, style_manager=None):
	match source:
		case Stylized_Span(style, text) if style is None:
			yield from get_style_operations(text, style_manager)

		case Stylized_Span(style, text) if style is not None:
			if style_manager:
				#yield from style_manager.render(style, text)
				yield from style_manager.render_push(style)
				yield from get_style_operations(text, style_manager)
				yield from style_manager.render_pop(style)

			else:
				yield Event.push('style', style)
				yield from get_style_operations(text, style_manager)
				yield Event.pop('style')

		case (list() | tuple()):
			for sub_item in source:
				yield from get_style_operations(sub_item, style_manager)

		case str():
			yield source

		case unhandled:
			raise Exception(repr(source))





def apply_style_operations(stylized_text, style):

	heap = State_Heap(
		invert = State_Stack('invert', False),
		faint = State_Stack('faint', False),
		bold = State_Stack('bold', False),
		italics = State_Stack('italics', False),
		underline = State_Stack('underline', False),
		filters = Filter_Stack('filters'),
		foreground_color = State_Stack('foreground_color'),
		background_color = State_Stack('background_color'),
	)

	result = list()
	for op in get_style_operations(stylized_text, style):
		match op:
			case Event.push(stack, value):
				 heap.lut[stack].push(value)

			case Event.pop(stack):
				 heap.lut[stack].pop()

			case str():
				state = heap.get_state()
				if result and result[-1].state == state:
					result[-1].text += op
				else:
					result.append(State_Span(state, op))

			case unmatched:
				raise Exception(op)
	return result
