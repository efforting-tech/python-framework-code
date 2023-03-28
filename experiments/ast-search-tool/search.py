import __main__
from __main__ import token_reference
from fnmatch import fnmatch
import re, time
import token as TT

#TODO - we should make a way where we could launch multiple clients and have them spread out the files. We could orchestrate it with the primary client. This way we could utilize multiprocessing.
#		one issue here might be if we are caring about the order of results, but in that case we can associate indices with those items (this may not even be relevant in this application).

#	The IPC interface could use streams and iterators where it would ask for pages just like a user, this way we can ask all services for a page each for instance and construct a local page from those.
#	However - this will probably use a tremendous amount of memory in the current implementation. A better option would be to do this after the C-DB.


if not hasattr(__main__, 'pending_query'):
	__main__.pending_query = None

if not hasattr(__main__, 'page_size'):
	__main__.page_size = 10

if not hasattr(__main__, 'pagination'):
	__main__.pagination = True

if not hasattr(__main__, 'query_history'):
	__main__.query_history = list()

def perform_search(code_registry, main_index, query):

	def present_result(result_index, ref):
		match ref:
			case token_reference():
				tok = ref.owner.token_markings[ref.index][2]
				row, col = tok.start
				floc = f'{str(ref.owner.path.relative_to("."))}:{row}'

				line = ref.owner.syntax_highlighted_source[row-1]

				mdesc = f'{line}'
				print(f'    {result_index:<5}{floc:50}{mdesc}')

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	def present_result_with_size(result_index, ref):
		match ref:
			case token_reference():
				tok = ref.owner.token_markings[ref.index][2]
				row, col = tok.start
				floc = f'{str(ref.owner.path.relative_to("."))}:{row}'

				line = ref.owner.syntax_highlighted_source[row-1]

				mdesc = f'{line}'
				print(f'    {result_index:<5}{floc:50}{mdesc}')
				print(f'       Size: {ref.owner.stat.st_size:,} bytes')

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	def present_result_with_mtime(result_index, ref):
		match ref:
			case token_reference():
				tok = ref.owner.token_markings[ref.index][2]
				row, col = tok.start
				floc = f'{str(ref.owner.path.relative_to("."))}:{row}'

				line = ref.owner.syntax_highlighted_source[row-1]

				mdesc = f'{line}'
				print(f'    {result_index:<5}{floc:50}{mdesc}')
				print(f'       Modified: {time.ctime(ref.owner.stat.st_mtime)}')

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	def present_identifier(result_index, item):
		count = len(main_index[item])
		print(f'    {result_index:<5}{item!r} - {count} references')

	def present_history(result_index, item):
		print(f'    {result_index:<5}{item}')

	def present_source_match(result_index, source):
		print(f'    {result_index:<5}{source.path.relative_to(".")} - {source.path.stat().st_size:,} bytes')

	def present_source_re_match(result_index, match, source):
		print(f'    {result_index:<5}{source.path.relative_to(".")} - {source.path.stat().st_size:,} bytes', match)

	def search_file(pattern):
		count = 0
		for source in code_registry.sources.values():
			if fnmatch(str(source.path.name), pattern):
				count += 1
				yield count, present_source_match, source

	def search_path(pattern):
		count = 0
		for source in code_registry.sources.values():
			if fnmatch(str(source.path), pattern):
				count += 1
				yield count, present_source_match, source

	def re_search_file(pattern):
		count = 0
		for source in code_registry.sources.values():
			if m := pattern.match(str(source.path.name)):
				count += 1
				yield count, present_source_re_match, m, source

	def re_search_path(pattern):
		count = 0
		for source in code_registry.sources.values():
			if m := pattern.match(str(source.path)):
				count += 1
				yield count, present_source_re_match, m, source

	def search_word(pattern):
		found_results = False
		count = 0
		for index_word, references in main_index.items():
			if fnmatch(index_word, pattern):
				for ref in references:
					found_results = True
					count += 1
					yield count, present_result, ref


	def search_comment(pattern):
		found_results = False
		count = 0
		for index_word, references in main_index.items():
			if fnmatch(index_word, pattern):
				for ref in references:
					match ref:
						case token_reference():
							tok = ref.owner.token_markings[ref.index][2]
							if tok.type == TT.COMMENT:
								found_results = True
								count += 1
								yield count, present_result, ref


	def search_no_comment(pattern):
		found_results = False
		count = 0
		for index_word, references in main_index.items():
			if fnmatch(index_word, pattern):
				for ref in references:
					match ref:
						case token_reference():
							tok = ref.owner.token_markings[ref.index][2]
							if tok.type != TT.COMMENT:
								found_results = True
								count += 1
								yield count, present_result, ref

	def show_identifiers():
		for count, item in enumerate(main_index, 1):
			yield count, present_identifier, item


	def show_history():
		count = 0
		for item in __main__.query_history:
			count += 1
			yield count, present_history, item

	def sort_by_size(query, reverse=False):
		result = list()
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ == 'present_source_re_match':
				match, source = args
				result.append((source.stat.st_size, index, presenter, *args))
			elif presenter.__name__ == 'present_source_match':
				[source] = args
				result.append((source.stat.st_size, index, presenter, *args))
			elif presenter.__name__ == 'present_result':
				[ref] = args
				result.append((ref.owner.stat.st_size, index, present_result_with_size, *args))
			else:
				raise Exception(presenter)

		count = 0
		for weight, index, *args in sorted(result, key=lambda i: i[0], reverse=reverse):
			count += 1
			yield count, *args

	def once_per_file(query):		#Later we should be able to modify the current filter chain since now we replace it
		visited = set()
		count = 0
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ == 'present_source_re_match':
				match, source = args
				if source not in visited:
					visited.add(source)
					count += 1
					yield count, presenter, *args
			elif presenter.__name__ == 'present_result':
				[ref] = args
				source = ref.owner
				if source not in visited:
					visited.add(source)
					count += 1
					yield count, presenter, *args

			elif presenter.__name__ == 'present_identifier':	#Does not apply
				count += 1
				yield count, presenter, *args
			else:
				raise Exception(presenter)


	def sort_by_name(query, reverse=False):
		result = list()
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ == 'present_source_re_match':
				match, source = args
				key = source.path.name, source.path.parent
				result.append((key, index, presenter, *args))
			elif presenter.__name__ == 'present_identifier':
				[identifier] = args
				key = identifier
				result.append((key, index, presenter, *args))
			else:
				raise Exception(presenter)

		count = 0
		for weight, index, *args in sorted(result, key=lambda i: i[0], reverse=reverse):
			count += 1
			yield count, *args


	def sort_by_refcount(query, reverse=False):
		result = list()
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ in ('present_source_re_match', 'present_result'):
				key = 1
				result.append((key, index, presenter, *args))
			elif presenter.__name__ == 'present_identifier':
				[identifier] = args
				key = len(main_index[identifier])
				result.append((key, index, presenter, *args))
			else:
				raise Exception(presenter)

		count = 0
		for weight, index, *args in sorted(result, key=lambda i: i[0], reverse=reverse):
			count += 1
			yield count, *args


	def sort_by_path(query, reverse=False):
		result = list()
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ == 'present_source_re_match':
				match, source = args
				result.append((source.path, index, presenter, *args))
			else:
				raise Exception(presenter)

		count = 0
		for weight, index, *args in sorted(result, key=lambda i: i[0], reverse=reverse):
			count += 1
			yield count, *args



	def sort_by_mtime(query, reverse=False):
		result = list()
		for index, presenter, *args in query:
			#ok, this is super ugly - we should first yield results then query them but now we yield calls to presenters - so we match them here
			#note that this is just to get sorting working for now, this must be fixed!

			if presenter.__name__ == 'present_source_re_match':
				match, source = args
				result.append((source.stat.st_mtime, index, presenter, *args))
			elif presenter.__name__ == 'present_source_match':
				[source] = args
				result.append((source.stat.st_mtime, index, presenter, *args))
			elif presenter.__name__ == 'present_result':
				[ref] = args
				result.append((ref.owner.stat.st_mtime, index, present_result_with_mtime, *args))		#NOTE - here we switch to a different presenter since we want to display what we sort by - but we should harmonize this to some API for presenting items
			else:
				raise Exception(presenter)

		count = 0
		for weight, index, *args in sorted(result, key=lambda i: i[0], reverse=reverse):
			count += 1
			yield count, *args

	def purge_registry(query, dry_run=False):
		sources_to_purge = set()
		for index, presenter, *args in query:
			if presenter.__name__ == 'present_source_match':
				[source] = args
				sources_to_purge.add(source)
			else:
				raise Exception(presenter)

		print(f'    Need to purge {len(sources_to_purge)} sources ...')

		keys_to_scrap = list()
		removed_ref_count = 0
		for key, old_refs in tuple(main_index.items()):

			new_refs = list()
			for ref in old_refs:
				match ref:
					case token_reference() if ref.owner in sources_to_purge:
						pass
					case _:
						new_refs.append(ref)

			if len(new_refs) == len(old_refs):
				pass
			elif new_refs:
				if not dry_run:
					main_index[key] = tuple(new_refs)
				removed_ref_count += len(old_refs) - len(new_refs)
			else:
				keys_to_scrap.append(key)

		print(f'    Removed {removed_ref_count} references')

		if not dry_run:
			for key in keys_to_scrap:
				del main_index[key]

		print(f'    Removed {len(keys_to_scrap)} keys')


		if not dry_run:
			for source in sources_to_purge:
				code_registry.sources.pop(source.path, None)	#I used pop just in case, not sure if multiple sources might resolve to the same path, most likely not. (loose thinking)

		print(f'    Removed {len(sources_to_purge)} sources')

		print('    Purge complete')


	def check_command():
		#This is just for testing
		match query.split():
			case ['exec', *args]:
				nonlocal code_registry
				exec(' '.join(args), {}, locals())
				return True

			case ['history']:
				__main__.pending_query = show_history()

			case ['show', 'current']:	#Debug
				print(repr(__main__.pending_query))
				return True

			case ['page', 'size', number]:
				__main__.page_size = int(number)
				return True

			case ['page', 'size']:
				print('    ', __main__.page_size)
				return True

			case ['pagination', 'on']:
				__main__.pagination = True
				return True

			case ['pagination', 'off']:
				__main__.pagination = False
				return True

			case ['abort']:
				__main__.pending_query = None
				return True

			case ['select', *selection]:
				#q, *args = __main__.query_history[-1]
				#__main__.pending_query = sort_by_size(q(*args))

				#print(get_selection(' '.join(selection)))
				print('    This is not implemented yet')	#we should use the nice parsing tools we experimented with

				return True

			case ['once', 'per', 'file']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = once_per_file(q(*args))

			case ['sort', 'size']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_size(q(*args))

			case ['sort', 'name']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_name(q(*args))

			case ['sort', 'reference', 'count']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_refcount(q(*args))

			case ['sort', 'path']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_path(q(*args))

			case ['sort', 'modified']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_mtime(q(*args))

			case ['reverse', 'sort', 'size']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_size(q(*args), True)

			case ['reverse', 'sort', 'name']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_name(q(*args), True)

			case ['reverse', 'sort', 'path']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_path(q(*args), True)

			case ['reverse', 'sort', 'modified']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_mtime(q(*args), True)

			case ['newest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_mtime(q(*args), True)

			case ['oldest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_mtime(q(*args), False)

			case ['smallest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_size(q(*args), False)

			case ['biggest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_size(q(*args), True)


			case ['most', 'frequent'] | ['commonest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_refcount(q(*args), True)

			case ['rarest']:
				q, *args = __main__.query_history[-1]
				__main__.pending_query = sort_by_refcount(q(*args))


			case ['purge', 'from', 'registry']:
				q, *args = __main__.query_history[-1]
				purge_registry(q(*args))
				return True

			case ['continue']:
				if not __main__.pending_query:
					print('    -= No pending query =-')

			case ['count']:
				q, *args = __main__.query_history[-1]
				count = 0
				for item in q(*args):
					count += 1
				print(f'    {count} items')
				return True

			case ['show', 'all']:
				q, *args = __main__.query_history[-1]
				for count, presenter, *positionals in q(*args):
					presenter(count, *positionals)
				else:
					print('    -= End of query =-')
					__main__.pending_query = None

				return True



			case ['identifier', 'count']:
				count = len(main_index)
				print(f'    {count} items')
				return True


			case ['show', 'identifiers']:
				__main__.pending_query = show_identifiers()
				__main__.query_history.append((show_identifiers,))



			case ['word', 'count']:
				count = len(set(map(str.lower, main_index)))
				print(f'    {count} items')
				return True

			case ['file', pattern]:
				__main__.pending_query = search_file(pattern)
				__main__.query_history.append((search_file, pattern))

			case ['comment', pattern]:
				__main__.pending_query = search_comment(pattern)
				__main__.query_history.append((search_comment, pattern))

			case ['code', pattern]:
				__main__.pending_query = search_no_comment(pattern)
				__main__.query_history.append((search_no_comment, pattern))

			case ['path', pattern]:
				__main__.pending_query = search_path(pattern)
				__main__.query_history.append((search_path, pattern))

			case ['re', 'file', pattern]:
				cp = re.compile(pattern)
				__main__.pending_query = re_search_file(cp)
				__main__.query_history.append((re_search_file, cp))

			case ['re', 'comment', pattern]:
				cp = re.compile(pattern)
				__main__.pending_query = re_search_comment(cp)
				__main__.query_history.append((re_search_comment, cp))

			case ['re', 'path', pattern]:
				cp = re.compile(pattern)
				__main__.pending_query = re_search_path(cp)
				__main__.query_history.append((re_search_file, cp))

			case ['word', word]:
				__main__.pending_query = search_word(word)
				__main__.query_history.append((search_word, word))

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')


	no_present = check_command()
	if no_present:
		return

	if __main__.pending_query:
		for count, presenter, *positionals in __main__.pending_query:
			presenter(count, *positionals)
			if __main__.pagination and count % __main__.page_size == 0:	#Pagination test
				break
		else:
			print('    -= End of query =-')
			__main__.pending_query = None

