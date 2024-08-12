from pathlib import Path
import importlib

from .. import __package__ as package_root



def get_resource_path(sub_path):
	return Path(__file__).parent / sub_path


class lazy_library_query:
	def __init__(self, package):
		self.package = package

	def query(self, data_path, pick=None):
		#print('DP', self.package, data_path)
		mod = importlib.import_module(f'.{data_path or ""}', package=self.package)

		if isinstance(pick, (tuple, list)):
			return [getattr(mod, p) for p in pick]
		elif isinstance(pick, str):
			return getattr(mod, pick)
		else:
			return mod

LZ = lazy_library_query(package_root)



def resolve_uri_lzq(query):
	data_path, sep, sub_query = query.partition('/')

	if sep:

		if sub_query.startswith('['):
			assert sub_query.endswith(']')
			return LZ.query(data_path, tuple(map(str.strip, sub_query[1:-1].split(','))))
		else:
			return LZ.query(data_path, sub_query)
	else:
		return LZ.query(data_path)




uri_resolvers = dict(
	lzq = resolve_uri_lzq
)

#TODO - use resolver?
def resolve_uri(uri):
	protocol, sep, query = uri.partition('://')
	assert sep


	return uri_resolvers[protocol.lower()](query)
