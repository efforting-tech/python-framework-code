from ...data_utils import is_type
from .xml_helpers import walk_xml_data_with_parents, make_xml_pretty
from collections import deque

class attribute:
	def process_attributes(self, processor):
		for attribute in self.attributes:
			yield processor(attribute)

class children:
	def process_children(self, processor):
		for child in self.children:
			yield processor(child)

	def remove_child(self, child):
		if isinstance(self.children, tuple):
			self.children = deque(self.children)

		self.children.remove(child)

	def strip_data(self, strip='\r\n\t '):
		to_remove = deque()
		for element, data in walk_xml_data_with_parents(self):
			data.value = data.value.strip('\r\n\t ')
			if not data.value:
				to_remove.append((element, data))

		for element, data in to_remove:
			element.remove_child(data)

	def walk_data(self):
		return walk_xml_data(self)

	def make_pretty(self):
		make_xml_pretty(self)


	def iter_children(self, instance_check=None, type_check=None):
		for child in self.children:
			def process_child():
				use_filtering = bool(instance_check or type_check)

				if instance_check:
					if isinstance(child, instance_check):
						yield child
						return
				elif type_check:
					if is_type(child, type_check):
						yield child
						return

				else:
					yield child

			yield from process_child()
