#These are high level functions that draw upon many of the lower level ones.
#it would be nice to have everything semantically grouped but that creates circular dependencies so we also have to have the concept of "levels".

from pathlib import Path
from ...data_utils import is_subclass
from .xml_templating import template_processor, positional_template, base_template_collection, bound_positional_template, template
from .xml_tokenizer import tokenizer
from . import xml_formatting as XF
from . import xml_rules as XR


def strip_data(item):
	if is_subclass(item, base_template_collection):
		for k in item.__dict__:
			if k.startswith('_'):
				continue
			strip_data(item.__dict__[k])
	elif isinstance(item, dict):
		tuple(map(strip_data, item.values()))

	elif isinstance(item, bound_positional_template):
		strip_data(item.template)

	elif isinstance(item, template):
		item.element.strip_data()

	else:
		raise TypeError(item)


def load_templates_from_string(data, template_factory = positional_template, placeholder_prefix = 'PLACEHOLDER', template_prefix = 'TEMPLATE', return_dict=False):
	t = tokenizer(XR.main)
	t.process(data)

	[doc] = t.element.pop_all()

	tp = template_processor(
		template_factory = template_factory,
		placeholder_prefix = placeholder_prefix,
		template_prefix = template_prefix,
		return_dict = return_dict,
	)

	return tp(doc)

def load_templates_from_path(path, template_factory = positional_template, placeholder_prefix = 'PLACEHOLDER', template_prefix = 'TEMPLATE', return_dict=False):
	return load_templates_from_string(
		Path(path).read_text(),
		template_factory = template_factory,
		placeholder_prefix = placeholder_prefix,
		template_prefix = template_prefix,
		return_dict = return_dict,
	)

def write_to_path(path, item):
	Path(path).write_text(XF.format(item))


def hacky_pretty_print(data):
	from lxml import etree
	tree = etree.fromstring(bytes(XF.format(data), 'utf-8'))
	result = etree.tostring(tree, encoding='unicode', pretty_print=True)
	print(XF.terminal_highlight(result))


def highlighted_print(data):
	print(XF.terminal_highlight(XF.format(data)))

