from . import mnemonic_ast as MAST
from ..core.dispatcher.aggregation import Result_List
import sys


#TODO - move these utilities
class Indention_Wrapper_Context:
	def __init__(self, target):
		self.target = target

	def __enter__(self):
		self.target.increase_indent()

	def __exit__(self, et, ev, tb):
		self.target.decrease_indent()

#Note that this one is different because it wraps instead of duckpunch (compared to /srv/datacore2/devilholk/Projects/test-framework-python-2/t10.py )
class Indention_Wrapper:
	def __init__(self, target=sys.stderr, level=0, indent_marker='  '):
		self.level = level
		self.indent_marker = indent_marker
		self.target = target

		self.pending = ''

	def write(self, text):
		self.pending += text
		before, sep, after = self.pending.partition('\n')

		if sep:
			self.target.write(f'{self.level * self.indent_marker}{before}\n')
			self.pending = after
		else:
			pass

	def flush(self):
		if self.pending:
			self.target.write(f'{self.level * self.indent_marker}{self.pending}')

		self.target.flush()

		self.pending = ''




	def increase_indent(self):
		self.level += 1

	def decrease_indent(self):
		self.level -= 1

	def indent(self):
		return Indention_Wrapper_Context(self)


class Dumper(Indention_Wrapper):

	def print(self, text, end='\n'):
		self.write(f'{text}{end}')

	def dump(self, r):
		match r:
			case MAST.Tree():
				self.print(f'{type(r).__qualname__}: {r.title!r}')
				with self.indent():
					self.dump(r.body)

			case Result_List():
				self.print(f'{type(r).__qualname__}: {r!r}')
				with self.indent():
					for sub_item in r.value:
						self.dump(sub_item)

			case unhandled:
				self.print(f'{type(r).__qualname__}: {r!r}')

