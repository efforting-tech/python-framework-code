'''

	Purpose: This sketch is to look into grabbing a specific git reference in order to create a representation of the AST for AST comparison.

	Note: these experiments should be run with cwd being the top level dir in the git (we could make sure this is the case later)



	List contents of tree-ish
		(rev could be a branch or tags/{tag} for instance)

		git ls-tree -r --name-only {rev}

	Get contents of tree-ish
		(file should be relative to git root)

		git show {rev}:{file}

'''

import subprocess, ast
from pathlib import Path, PurePath


def get_files_by_revision(rev):
	proc = subprocess.Popen(('git', 'ls-tree', '-r', '--name-only', rev), stdout=subprocess.PIPE)
	stdout, stderr = proc.communicate(b'')
	return tuple(PurePath(str(p, 'utf-8', 'surrogateescape')) for p in stdout.split(b'\n'))


def get_file_contents_by_revision(file, rev):
	proc = subprocess.Popen(('git', 'show', f'{rev}:{file}'), stdout=subprocess.PIPE)
	stdout, stderr = proc.communicate(b'')
	return stdout


class id_map:
	def __init__(self):
		self.by_local_id = dict()
		self.by_foreign_id = dict()
		self.pending_id = 1

	def register(self, foreign_id):
		if foreign_id in self.by_foreign_id:
			return

		new_id = self.pending_id
		self.by_foreign_id[foreign_id] = new_id
		self.by_local_id[new_id] = foreign_id
		self.pending_id += 1
		return new_id


#Create map of objects in the ast module
ast_directory = id_map()
for item in ast.__dict__.values():
	if isinstance(item, type) and issubclass(item, ast.AST):
		ast_directory.register(item)


def serialize_ast(node):
	if isinstance(node, ast.AST):
		node_id = ast_directory.by_foreign_id[type(node)]
		return (node_id, *(serialize_ast(getattr(node, f)) for f in node._fields))
	elif isinstance(node, list):
		return (-1, *(serialize_ast(sub_node) for sub_node in node))	#TODO - use constant for type
	else:
		return repr(node)


def get_type(artifact):
	node_id, *remaining = artifact

	if node_id == -1:
		return list

	return ast_directory.by_local_id[node_id]


def get_type_and_remaining(artifact):
	node_id, *remaining = artifact

	if node_id == -1:
		return list, remaining

	return ast_directory.by_local_id[node_id], remaining


def unserialize_ast(item):

	if isinstance(item, (tuple, list)):

		node_type, remaining = get_type_and_remaining(item)
		if node_type is list:
			return [unserialize_ast(r) for r in remaining]
		else:
			return node_type(*(unserialize_ast(r) for r in remaining))

	else:
		return ast.literal_eval(item)

def walk_serialized_ast(item):
	yield item

	if isinstance(item, (tuple, list)):

		node_id, *remaining = item
		for sub_item in remaining:
			yield from walk_serialized_ast(sub_item)


test_tag = 'tags/test-doc-sync-1'

files = get_files_by_revision(test_tag)

# for file in files:
# 	if file.suffix == '.py':
# 		file_contents = get_file_contents_by_revision(PurePath('.') / file, test_tag)

# 		tree = ast.parse(file_contents)

# 		res = serialize_ast(tree.body)
# 		print(file, res)


fc1 = get_file_contents_by_revision('library/data_directory.py', test_tag)
#fc2 = get_file_contents_by_revision('library/data_directory.py', 'development')

s1 = serialize_ast(ast.parse(fc1))
#s2 = serialize_ast(ast.parse(fc2))

t1 = unserialize_ast(s1)
#t2 = unserialize_ast(s2)

def extract_artifacts(artifact, meta, parent=None, artifact_nodes = {ast.Module, ast.FunctionDef, ast.ClassDef, ast.Assign}):
	def process_item(name, body, yield_artifact=False):
		if yield_artifact:
			yield name, artifact

		for body_item in body:
			for sub_path, sub_artifact in extract_artifacts(body_item, meta, artifact, artifact_nodes=artifact_nodes):
				 yield f'{name}.{sub_path}', sub_artifact

	node_type = type(artifact)
	if parent:
		parent_type = type(parent)
	else:
		parent_type = None

	if node_type in artifact_nodes:	#First we check if we care about the node

		#Then we extract info
		if node_type is ast.Module:
			yield from process_item(meta.__name__, artifact.body, yield_artifact=True)

		elif node_type in {ast.FunctionDef, ast.ClassDef}:
			yield from process_item(artifact.name, artifact.body, yield_artifact=True)

		elif node_type is ast.Assign:
			for target in artifact.targets:
				target_type = type(target)
				if target_type is ast.Attribute:
					pass
				elif target_type is ast.Name:

					if parent_type is ast.Module:
						raise Exception(target.id)
					else:
						pass	#We skip assignments that are not module level

				else:
					raise NotImplementedError(target)

		else:
			raise NotImplementedError(f'Unhandled node type: {node_type}')

	else:
		pass



class namespace:
	def __init__(self, **values):
		self._data = values

	def __getattr__(self, key):
		return self._data[key]


def sphinx_table(table, columns):
	column_widths = tuple(max(len(row[c]) for row in [columns] + table) for c in range(len(table[0])))

	sep_format = f'   '.join('=' * c for c in column_widths)
	row_format = f'   '.join(f'{{:<{c}s}}' for c in column_widths)
	print(sep_format)
	print(row_format.format(*columns))
	print(sep_format)
	for row in table:
		print(row_format.format(*row))
	print(sep_format)




table = list()
for path, artifact in extract_artifacts(t1, namespace(__name__ = 'data_directory')):
#	table.append((f'``{path}``', f':class:`ast.{type(artifact).__name__}`'))
	table.append((type(artifact).__name__, path))

#sphinx_table(table, ('Artifact type', 'Path'))







#This is not strictly necessary but it would be kinda neat.
#Let's see if we can calculate something akin to a Levenshtein distance between the trees

# see https://link.springer.com/chapter/10.1007/978-3-319-68474-1_11

# We did have a thought of just putting all the serial pieces into a hash map for comparison


# import json
# print()

# print(ast.unparse(ast.fix_missing_locations(unserialize_ast(json.loads(json.dumps(s1))))))
# exit()

# hm1 = set(walk_serialized_ast(s1))
# hm2 = set(walk_serialized_ast(s2))

# for item in hm2 - hm1:
# 	print(item)
# 	print()

# #for item in walk_serialized_ast(s1):
# #	print(item)




# #print(ast.dump(t1))
# #print(ast.unparse(ast.fix_missing_locations(t1)))

