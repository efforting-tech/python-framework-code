#Improved and modularized version of t2.py and t3.py
from efforting.mvp6.document import create_line_listing_document_from_str
from efforting.mvp6.document.settings.indention import Indention_Mode

from efforting.mvp6.text.styling import presets
from efforting.mvp6.text.styling import Event, HSV

from efforting.mvp6.text.styling.terminal import stylize_and_render_document


l2 = create_line_listing_document_from_str('''
	Hello World!\x07\x07\x07
		Other thing
	  		More things
			   	Even more things\r
	 	Hope you are fine
		You are, right?
''', normalize_block = True)


import re	#Demonstrate defining custom styles and also how to inject them as re-match-spans
			#Note: later one should also be able to do row:col based spans

hl_spans = list()
for m in re.compile(r'thing').finditer(l2.to_str()):
	hl_spans.append((m, 'highlight'))

for m in re.compile(r'more').finditer(l2.to_str()):
	hl_spans.append((m, 'hl2'))

presets.fruity.define_style('highlight',
	(Event.push('invert', True),),
	(Event.pop('invert'),),
)

presets.fruity.define_style('hl2',
	(Event.push('bold', True), Event.push('foreground_color', HSV(0.22, 1, 1))),
	(Event.pop('bold'), Event.pop('foreground_color')),
)

#Notice that this test will fail if we update any styles
expected_output = (
	'\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m1\x1b[39m \x1b[38;2;163;204;122mHello\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mWorld!\x1b[39m\x1b[38;2;204;104;61m␇␇␇\x1b[39m\x1b[38;2;10;51;26m↵'
	'\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m2\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mOther\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122;7mthing\x1b[39;27m\x1b[38;2;10;51;26m↵'
	'\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m3\x1b[39m \x1b[38;2;10;51;26m··🬇🬃🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mMore\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122;7mthing\x1b[39;27m\x1b[38;2;163;204;122ms\x1b[39m\x1b[38;2;10;51;26m↵'
	'\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m4\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃🬇🬋🬋🬃···🬃\x1b[39m\x1b[38;2;163;204;122mEven\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;173;255;0;1mmore\x1b[39;22m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122;7mthing\x1b[39;27m\x1b[38;2;163;204;122ms\x1b[39m\x1b[38;2;204;104;61m␍\x1b[39m\x1b[38;2;10;51;26m↵'
	'\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m5\x1b[39m \x1b[38;2;10;51;26m·🬇🬋🬃\x1b[39m\x1b[38;2;163;204;122mHope\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122myou\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mare\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mfine\x1b[39m\x1b[38;2;10;51;26m↵'
	'\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m6\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mYou\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mare,\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mright?\x1b[39m'
)

assert stylize_and_render_document(l2, presets.fruity, highlight_spans=hl_spans) == expected_output
