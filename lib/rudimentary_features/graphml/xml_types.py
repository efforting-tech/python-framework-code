from . import xml_interface as interface
from collections import deque

#Note - cdata can be kinda weird: https://stackoverflow.com/questions/223652/is-there-a-way-to-escape-a-cdata-end-token-in-xml/223782#223782

class base_element:
	pass

class base_attribute:
	pass

class meta_element(base_element, interface.attribute):
	def __init__(self, tag, attributes=None):
		self.tag = tag
		self.attributes = deque() if attributes is None else attributes

	def __repr__(self):
		return f'<{self.__class__.__qualname__} {self.tag!r} #A {len(self.attributes)}>'

class element(base_element, interface.children, interface.attribute):
	def __init__(self, prefix, tag, attributes=None, children=None):
		self.prefix = prefix
		self.tag = tag
		self.attributes = deque() if attributes is None else attributes
		self.children = deque() if children is None else children

	def __repr__(self):
		return f'<{self.__class__.__qualname__} {self.prefix!r}:{self.tag!r} #A {len(self.attributes)} #C {len(self.children)}>'

class document(base_element, interface.children):
	def __init__(self, children=None):
		self.children = deque() if children is None else children

	def __repr__(self):
		return f'<{self.__class__.__qualname__} #C {len(self.children)}>'

class fragment(base_element, interface.children):
	def __init__(self, children=None):
		self.children = deque() if children is None else children

	def __repr__(self):
		return f'<{self.__class__.__qualname__} #C {len(self.children)}>'

class fragment_from_iterator(base_element):
	def __init__(self, iterator):
		self.iterator = iterator

	def __repr__(self):
		return f'<{self.__class__.__qualname__} {self.iterator!r}>'

class data:
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return f'<{self.__class__.__qualname__} #D {len(self.value)}>'

class comment:
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return f'<{self.__class__.__qualname__} #D {len(self.value)}>'


class reference:
	def __init__(self, id):
		self.id = id

	def __repr__(self):
		return f'<{self.__class__.__qualname__} {self.id!r}>'


class attribute_name:
	def __init__(self, prefix, name):
		self.prefix = prefix
		self.name = name

class attribute(base_attribute):
	def __init__(self, prefix, name, value):
		self.prefix = prefix
		self.name = name
		self.value = value

	def __repr__(self):
		return f'<{self.__class__.__qualname__} {self.prefix!r}:{self.name!r} = {self.value!r}>'


