from .actions import instantiate
from pathlib import _Flavour, PurePath, PurePosixPath, PureWindowsPath, Path

@instantiate
class _data_path_flavour(_Flavour):
	sep = '.'
	altsep = ''
	has_drv = False

	def splitroot(self, part, sep=sep):
		if part and part[0] == sep:
			stripped_part = part.lstrip(sep)
			return '', sep, stripped_part
		else:
			return '', '', part

	def casefold(self, s):
		return s

	def casefold_parts(self, parts):
		return parts

	def compile_pattern(self, pattern):
		return re.compile(fnmatch.translate(pattern)).fullmatch

	def is_reserved(self, parts):
		return False


class data_path(PurePath):
	_flavour = _data_path_flavour
	__slots__ = ()

	def __repr__(self):	#__repr__ will use the wrong separator (have not investigated why). Here is a hack to fix that.
		return f'{self.__class__.__qualname__}({str(self)!r})'
