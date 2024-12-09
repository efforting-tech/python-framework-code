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
			return self.line_view.get_min_indent()

	def iter_nodes(self):
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


	@property
	def body(self):
		print(self.str_lines)
		if self.title:
			return Tree_View_Interface(self.line_view, self.index+1, self.length-1, False)

	@property
	def str_lines(self):
		return tuple(l.text for l in self.line_view.lines[self.index:self.index+self.length])

	@property
	def sub_view(self):
		return self.line_view[self.index:self.index+self.length]


t = Tree_View_Interface(source)


#TODO - current issue is that when we dispatch tree we get empty nodes that we fail on

from efforting.mvp6._template_bootstrap_layer.processor import main
r = main.dispatcher.dispatch_tree(t)
