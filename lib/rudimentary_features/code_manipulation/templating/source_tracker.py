#TODO - move this module to right place
import time
from .... import type_system as RTS
from ....type_system.bases import public_base
from ....type_system.features import method_with_specified_settings
import linecache

class source_info(public_base):
	tracker = RTS.positional()
	file_id = RTS.positional()
	filename = RTS.positional()
	source_code = RTS.positional(default=None)
	created = RTS.factory(time.time)

	# def update(self, **fields):
	# 	for key, value in fields.items():
	# 		if key in self.tracker.do_not_track:
	# 			continue
	# 		setattr(self, key, value)

	def update_source(self, source_code):
		self.source_code = source_code
		if self.tracker.update_linecache and self.source_code:
			linecache.cache[self.file_id] = (len(self.source_code), None, self.source_code.split('\n'), self.filename)

	def purge(self):
		if self.tracker.update_linecache:
			linecache.cache.pop(self.file_id, None)
		self.tracker.registry.pop(self.file_id)

class source_tracker(public_base):
	pattern = RTS.setting('<tracked-{id}>')
	#do_not_track = RTS.setting(('constants', 'globals', 'locals', 'reverse_mapping_index', 'stack_offset'))
	update_linecache = RTS.setting(True)
	registry = RTS.setting(factory=dict)

	def register_new_file(self, filename, source_code=None):
		pending_id = len(self.registry)
		file_id = self.pattern.format(id = pending_id)
		result = self.registry[file_id] = source_info(self, file_id, filename)

		if source_code:
			result.update_source(source_code)

		return result

