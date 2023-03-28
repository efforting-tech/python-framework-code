
from efforting.mvp4 import rudimentary_type_system as RTS
from efforting.mvp4.rudimentary_type_system.bases import public_base

from efforting.mvp4.development_utils.introspection.package import load_package
from highlight_helper import get_highlighted_terminal_from_lines


class line_match(public_base):
	module = RTS.positional()
	line = RTS.positional()

	def present(self):
		print(self.module.full_name)
		print(self.module.syntax_highlighted_source[self.line-1])
		print()

class module_information(public_base):
	full_name = RTS.positional()
	path = RTS.positional()
	stat = RTS.positional()
	source = RTS.positional()
	ast = RTS.positional()
	_syntax_highlighted_source = RTS.state(None)

	# @property
	# def source_lines(self):
	# 	return self.source.split('\n')

	@property
	def syntax_highlighted_source(self):
		if (v := self._syntax_highlighted_source) is not None:
			return v

		self._syntax_highlighted_source = get_highlighted_terminal_from_lines(self.source_lines)
		# We need to match here - we are doing this in the colorized_traceback thing - we should check that.

		return self._syntax_highlighted_source

	def search(self, text):
		for index, line in enumerate(self.source_lines, 1):
			if text in line:
				yield line_match(self, index)

class module_directory(public_base):
	modules = RTS.field(factory=dict)

	@classmethod
	def from_package_name(cls, pkg_name):

		pkg = load_package(pkg_name)
		module_registry = dict()
		for module in pkg.registry.values():
			module_registry[module.full_name] = module_information(module.full_name, module.path, module.stat, module.source, module.ast)

		return cls(module_registry)


	def search(self, text):
		for module in self.modules.values():
			yield from module.search(text)

