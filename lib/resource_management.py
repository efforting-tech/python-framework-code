from pathlib import Path
from .string_utils import str_check_prefix

def get_resource_path(subpath):
	return Path(__file__).parent / 'resources' / subpath


def get_path(path):
	if resource_path := str_check_prefix(path, 'libres://', True):
		return get_resource_path(resource_path)
	else:
		return Path(path)
