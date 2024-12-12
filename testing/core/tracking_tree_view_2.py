
#This is testing out a tracking tree view that we need in order to continue matcher_factory_test6.py
from efforting.mvp6.core.text import Immutable_Line_View
from efforting.mvp6.core import record as R



#TODO debug printer for text blocks


#TODO - move to simple text presentation module
def render_non_printables(text, tab_width=4, format_control_character=lambda x: f'{x}', format_line_number=lambda n:f'{n:03}┊', start=1):
	line_no = start
	result = ''

	for line in text.splitlines():
		result += format_line_number(line_no)
		line_len = 0
		for c in line:
			if c == '\t':
				tl = tab_width - line_len % tab_width
				line_len += tl
				if tl == 1:
					result += format_control_character('━')
				else:
					result += format_control_character(f'╺{"━"*(tl-2)}╸')

			elif c == ' ':
				result += format_control_character('·')
				line_len += 1

			else:
				result +=  c
				line_len += 1

		result += format_control_character('⏎') + '\n'
		line_no += 1


	return result




source = Immutable_Line_View.from_str('''


	Hello

		World! How Are you?

	Zup!
		stuff

''')



#Maybe we really need to make some sort of difference whether it is a tree or a node
#We should possibly also track levels and stuff for child views instead of trying to figure it out
#TODO: We should rewrite this viewer in tracking_tree_view_3.py and make sure it works properly
class Tree_View_Interface(R.Record):
	line_view: R.Field()
	index: R.Field() = 0
	length: R.Field() = 0
	empty: R.Field() = False

	@property
	def title(self):
		return self.line_view[self.index].text.strip()

	@property
	def level(self):
		if self.title:
			return self.line_view[self.index].indent
		else:
			return self.sub_view.get_min_indent()

	def iter_nodes(self):
		if self.empty:
			return

		local_indent = self.level
		index = self.index
		last_root_index = None
		for local_index, i in enumerate(self.line_view):
			if not i.value:
				continue

			if i.indent < local_indent:
				break

			elif i.indent == local_indent:
				if last_root_index is not None:
					if last_root_index > index:
						yield Tree_View_Interface(self.line_view, index, last_root_index - index, True)
					index = local_index
					yield Tree_View_Interface(self.line_view, last_root_index, local_index-last_root_index, False)
				last_root_index = local_index

		if last_root_index is not None:
			if last_root_index > index:
				yield Tree_View_Interface(self.line_view, index, last_root_index - index, True)

			last_content_index = self.line_view.last_line_index_with_content
			yield Tree_View_Interface(self.line_view, last_root_index, last_content_index-last_root_index, False)
			if local_index > last_content_index:
				yield Tree_View_Interface(self.line_view, last_content_index, local_index-last_content_index, True)

	def to_str(self):
		return '\n'.join(l.to_str() for l in self.line_view.lines[self.index:self.index+self.length])

	@property
	def body(self):
		if self.title:
			return Tree_View_Interface(self.line_view, self.index+1, self.length-1, False)

	@property
	def str_lines(self):
		return tuple(l.to_str() for l in self.line_view.lines[self.index:self.index+self.length])

	@property
	def sub_view(self):
		return self.line_view[self.index:self.index+self.length]

t = Tree_View_Interface(source, length=len(source.lines))



#TODO - current issue is that when we dispatch tree we get empty nodes that we fail on

#DEBUG: Currently the problem is that we get an empty body because we don't have a title

def dump_tree(t, i=0):
	import textwrap
	print(f"{'  '*i}{t}")
	print(textwrap.indent(render_non_printables(t.to_str()), '  '*i))

	for sub_node in t.iter_nodes():
		dump_tree(sub_node, i+1)




#dump_tree(t)

#from efforting.mvp6._template_bootstrap_layer.processor import main
#print('...')
#r = main.dispatcher.dispatch_tree(t)
