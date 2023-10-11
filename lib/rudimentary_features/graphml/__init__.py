from . import xml_types
from . import xml_helpers as XH
from . import xml_templating as XT
from . import xml_highlevel as XHL
from ...type_system.bases import standard_base
from ... import type_system as RTS
from ...rudimentary_types.prefixed_key_registry import prefixed_key_registry

from ...resource_management import get_path
from ...development_utils import cexp	#TODO move


class graphml_interface(standard_base):
	load_templates = RTS.field(default=())

	data_keys = RTS.factory(prefixed_key_registry, 'd')
	nodes = RTS.factory(prefixed_key_registry, 'n')
	edges = RTS.factory(prefixed_key_registry, 'e')

	node_graphics = RTS.state()
	edge_graphics = RTS.state()
	node_urls = RTS.state()
	templates = RTS.state(factory=XT.base_template_collection)

	@RTS.initializer
	def init(self):
		self.node_graphics = self.data_keys.register_using_factory(lambda id: XH.element('key', {'for': 'node', 'id': id, 'yfiles.type': 'nodegraphics'}))
		self.edge_graphics = self.data_keys.register_using_factory(lambda id: XH.element('key', {'for': 'edge', 'id': id, 'yfiles.type': 'edgegraphics'}))
		self.node_urls = self.data_keys.register_using_factory(lambda id: XH.element('key', {'attr.name': 'url', 'attr.type': 'string', 'for': 'node', 'id': id}))


		for path in self.load_templates:
			pending_templates = XHL.load_templates_from_path(get_path(path), return_dict=True)
			XHL.strip_data(pending_templates)
			self.templates.__dict__.update(pending_templates)

	def group(self, registry, label, fill_color, label_color):
		group_registry = None
		def inner(id):
			nonlocal group_registry
			group_registry = prefixed_key_registry(f'{id}::')
			return XH.element('node',
				('id', id),
				('yfiles.foldertype', 'group'),
				XH.element('data',
					('key', self.node_graphics),
					self.templates.group_content(
						fill_color,
						label_color,
						XH.data(label),
					),
				),

				XH.element('graph',
					('id', f'{id}:'),
					XH.fragment_from_iterator(group_registry),
				)
			)

		registry.register_using_factory(inner)

		return group_registry


	def rectangle_node(self, registry, color, label, url=None):
		def inner(id):

			if url:
				url_node = XH.element('data', XH.data(url), key=self.node_urls)
			else:
				url_node = None

			result = self.templates.node(id,
				XH.fragment(
					XH.element('data',
						self.templates.shape_node(color, XH.data(label)),
						key=self.node_graphics,
					),
					*cexp(url_node, url_node),
				)
			)

			# if url:
			# 	from . import xml_formatting as XF
			# 	print(XF.format(result))

			return result

		return registry.register_using_factory(inner)


	def edge(self, source, dest, edge_color, label_color, label):
		return self.edges.register_using_factory(lambda id:
			self.templates.edge(id,
				source,
				dest,
				XH.fragment(
					XH.element('data', {'key': self.edge_graphics},
						self.templates.edge_shape(
							edge_color,
							label_color,
							XH.data(label)
						),
					),
				),
			)
		)


	def render_xml(self):
		return self.templates.graph(
			XH.fragment(
				*self.data_keys,
				#XH.comment('Experimental'),
				self.templates.graph_def('G',
					XH.fragment(
						*self.nodes,
						*self.edges,
					),
				),
			)
		)

