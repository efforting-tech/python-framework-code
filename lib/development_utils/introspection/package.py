import pkgutil, ast, glob
from pathlib import Path

from ...rudimentary_type_system.bases import standard_base
from ... import rudimentary_type_system as RTS

class common_interface(standard_base):

	def find_module_in_path(self, path, name):
		if result := self.maybe_find_module_in_path(path, name):
			return result
		else:
			raise exception(path, name)

	def module_by_path(self, path):
		#A bit of a hack, maybe we can improve on this or find a better way to resolve relative imports
		for value in self.root.registry.values():
			if value.path == path:
				return value
			#if value.parent and value.parent.path.parent == path and value.name == name:
				#return value


	def maybe_find_module_in_path(self, path, name):
		#A bit of a hack, maybe we can improve on this or find a better way to resolve relative imports

		name_pieces = name.split('.')
		if len(name_pieces) > 1:
			for i in range(len(name_pieces)-1):
				path = path.parent
			path /= Path(*name_pieces[:-1])
			name = name_pieces[-1]

		for value in self.root.registry.values():
			if value.parent and value.parent.path.parent == path and value.name == name:
				return value


	def get_relative_path(self, levels, module=None):
		#This whole function is a mess
		#It works for this project but we should make it proper
		path = self.path

		ref = self
		for i in range(levels):
			path = path.parent

		if module:
			for part in module.split('.'):
				path = self.find_module_in_path(path, part).path.parent

		return path

	def get_relative(self, levels, module=None):
		#DEPRECATED
		#This whole function is a mess
		#It works for this project but we should make it proper
		path = self.path

		ref = self
		for i in range(levels):
			path = path.parent

		#A bit of a hack, maybe we can improve on this or find a better way to resolve relative imports
		def find_module_in_path(path, name):
			for value in self.root.registry.values():
				if value.parent and value.parent.path.parent == path and value.name == name:
					return value

			raise Exception(path, name)

		def find_module_by_path(path):
			for value in self.root.registry.values():
				if value.path == path:
					return value

			raise Exception(path)

		if module:
			for part in module.split('.'):
				ref = find_module_in_path(path, part)
				path /= part	#Descend into subpath
		else:

			print(find_module_by_path(path))

			if self.name == 'orchestration':
				print(self.full_name, levels, module)

			raise Exception()

		assert ref
		return ref

	@RTS.cached_property()
	def source(self):
		return self.spec.loader.get_source(self.full_name)

	@property
	def stat(self):
		return self.path.stat()

	@RTS.cached_property()
	def ast(self):
		return ast.parse(self.source)

	@RTS.cached_property()
	def ast_lut(self):
		lut = dict()

		def register(key, value):
			assert isinstance(key, str)
			if key in lut:
				print(f'Warning - overwriting {key!r} in {self.full_name!r} with {value!r}')
			lut[key] = value

		for node in self.ast.body:
			if isinstance(node, ast.Assign):
				#TODO - implement
				#for t in iter_targets(item):
				pass

			elif isinstance(node, (ast.Import, ast.ImportFrom)):
				for n in node.names:
					register(n.asname or n.name, (node, n))

			elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
				register(node.name, node)

		return lut

	@property
	def root(self):
		if self.parent:
			return self.parent.root
		else:
			return self


class package_info(common_interface):
	name = RTS.positional()
	path = RTS.positional()
	spec = RTS.positional()
	submodule_search_locations = RTS.positional()
	parent = RTS.field(default=None)

	sub_modules = RTS.factory(dict)
	registry = RTS.factory(dict)



	@property
	def full_name(self):
		return self.name

	def glob(self, pattern='**/*.py'):
		files = set()
		for pe in self.submodule_search_locations:
			files |= set(map(Path, glob.glob(f'{pe}/{pattern}', recursive=True)))

		return files

	def get_registered_files(self):
		return set(i.path for i in self.registry.values())

	def get_orphaned_source_files(self):
		return self.glob() - self.get_registered_files()

	@RTS.initializer
	def initialize(self):
		self.registry[self.full_name] = self

		def inner_walk(parent, path):
			for sub_module in pkgutil.iter_modules(path):
				full_name = f'{parent.full_name}.{sub_module.name}'
				spec = sub_module.module_finder.find_spec(full_name)
				info = parent.sub_modules[sub_module.name] = module_info(parent, sub_module.name, sub_module, spec)
				yield info

				if spec.submodule_search_locations:
					yield from inner_walk(info, spec.submodule_search_locations)

		for m in inner_walk(self, self.submodule_search_locations):
			self.registry[m.full_name] = m

class module_info(common_interface):
	parent = RTS.positional()
	name = RTS.positional()
	info = RTS.positional()
	spec = RTS.positional()

	sub_modules = RTS.factory(dict)

	@property
	def path(self):
		return Path(self.spec.origin)

	@property
	def full_name(self):
		return f'{self.parent.full_name}.{self.name}'


#TODO - make this a class method of package_info
def load_package(name):
	pkg_module = pkgutil.resolve_name(name)
	return package_info(pkg_module.__name__, Path(pkg_module.__spec__.origin), pkg_module.__spec__, pkg_module.__path__)

def check_orphaned_files(pkg):
	#Note - this does not suggest directories that are missing __init__.py if they don't contain any python files at all.
	#	we should improve this
	if orphaned_source_files := pkg.get_orphaned_source_files():
		orphaned_source_directories = set(file.parent for file in orphaned_source_files)
		print(f'There are {len(orphaned_source_files)} orphaned source files in {len(orphaned_source_directories)} directories')

		[library_root] = pkg.submodule_search_locations		#Assume there is only one search location
		for dir in sorted(orphaned_source_directories):
			if not (dir / '__init__.py').exists():
				print(f'    {dir.relative_to(library_root)} is missing __init__.py')

	return orphaned_source_files
