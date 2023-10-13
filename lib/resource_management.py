from pathlib import Path
from .string_utils import str_check_prefix
import sys

def get_resource_path(subpath):
	return Path(__file__).parent / 'resources' / subpath


def get_path(path):
	if resource_path := str_check_prefix(path, 'libres://', True):
		return get_resource_path(resource_path)
	else:
		return Path(path)

def get_local_module_path(subpath):
	[module_path] = sys._getframe(1).f_locals['__path__']	#TODO - define convention, should we put stuff in a local resources directory or just mix it in with the python files?
	return Path(module_path) / subpath