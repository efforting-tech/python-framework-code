from . import xml_types as XML
from collections import deque

def split_prefix(item):
	pieces = item.split(':', 1)
	if len(pieces) == 1:
		return None, pieces[0]
	else:
		return pieces


#NOTE - we have a circular import here which is fine as long as access the globals of this module after initialization
#	that is, we can have a function returning XML.data(...) but we can't simple assign something to XML.data
#	We should of course fix this but will leave this for now


def data(value):
	return XML.data(value)

def comment(value):
	return XML.comment(value)

def fragment(*children):
	return XML.fragment(children)

def fragment_from_iterator(iterator):
	return XML.fragment_from_iterator(iterator)

def element(tag, *sub_items, **additional_attributes):

	attributes = deque()
	children = deque()

	for item in sub_items:
		if isinstance(item, (XML.base_element, XML.comment, XML.data)):	#note - should comment inherit base_element?
			children.append(item)
		elif isinstance(item, XML.base_attribute):
			attributes.append(item)
		elif isinstance(item, dict):
			for key, value in item.items():
				attributes.append(XML.attribute(*split_prefix(key), value))
		elif isinstance(item, tuple):
			key, value = item
			attributes.append(XML.attribute(*split_prefix(key), value))
		else:
			raise TypeError(item)


	for key, value in additional_attributes.items():
		attributes.append(XML.attribute(*split_prefix(key), value))

	return XML.element(*split_prefix(tag), attributes, children)





def make_xml_pretty(item):
	#TODO - figure out what we want to do here

	raise NotImplementedError
	# if isinstance(item, (XML.document, XML.fragment)):
	# 	pending_children = deque()

	# 	for child in item.children:


	# else:
	# 	raise TypeError(item)

def walk_xml(item, attributes=False):
	if isinstance(item, (XML.document, XML.fragment)):
		yield item
		for child in item.children:
			yield from walk_xml(child, attributes)

	elif isinstance(item, (XML.meta_element, XML.data, XML.comment, XML.attribute)):
		yield item

	elif isinstance(item, XML.element):
		yield item
		if attributes:
			for attribute in item.children:
				yield from walk_xml(attribute, attributes)

		for child in item.children:
			yield from walk_xml(child, attributes)
	else:

		raise TypeError(item)


def walk_xml_with_parents(item, attributes=False, parent=None):
	if isinstance(item, (XML.document, XML.fragment)):
		yield parent, item
		for child in item.children:
			yield from walk_xml_with_parents(child, attributes, item)

	elif isinstance(item, (XML.meta_element, XML.data, XML.comment, XML.attribute)):
		yield parent, item

	elif isinstance(item, XML.element):
		yield parent, item
		if attributes:
			for attribute in item.children:
				yield from walk_xml_with_parents(attribute, attributes, item)

		for child in item.children:
			yield from walk_xml_with_parents(child, attributes, item)
	else:

		raise TypeError(item)

def walk_xml_data(item):
	for item in walk_xml(item):
		if isinstance(item, XML.data):
			yield item


def walk_xml_data_with_parents(item):
	for parent, item in walk_xml_with_parents(item):
		if isinstance(item, XML.data):
			yield parent, item







