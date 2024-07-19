#Testing text_tree
from efforting.mvp6.document import create_line_listing_document_from_str, create_text_tree_document_from_str
from efforting.mvp6.text.styling import presets
from efforting.mvp6.text.styling.terminal import stylize_and_render_document

t = create_text_tree_document_from_str('''
	Hello World!\x07\x07\x07
		Other thing
			More things
				Even more things\r

		Hope you are fine
		You are, right?

	Second?
		Stuf!

	Third!?

''', normalize_block = True)


expected = [
	'\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m1\x1b[39m \x1b[38;2;163;204;122mHello\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mWorld!\x1b[39m\x1b[38;2;204;104;61m␇␇␇\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m2\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mOther\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mthing\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m3\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mMore\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mthings\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m4\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃🬇🬋🬋🬃🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mEven\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mmore\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mthings\x1b[39m\x1b[38;2;204;104;61m␍\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m5\x1b[39m \x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m6\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mHope\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122myou\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mare\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mfine\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m7\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mYou\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mare,\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mright?\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m8\x1b[39m \x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m9\x1b[39m \x1b[38;2;163;204;122mSecond?\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m0\x1b[39m\x1b[38;2;255;63;178m10\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mStuf!\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m0\x1b[39m\x1b[38;2;255;63;178m11\x1b[39m \x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m0\x1b[39m\x1b[38;2;255;63;178m12\x1b[39m \x1b[38;2;163;204;122mThird!?\x1b[39m',
	('Other thing', '\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m3\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mMore\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mthings\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m4\x1b[39m \x1b[38;2;10;51;26m🬇🬋🬋🬃🬇🬋🬋🬃🬇🬋🬋🬃\x1b[39m\x1b[38;2;163;204;122mEven\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mmore\x1b[39m\x1b[38;2;10;51;26m·\x1b[39m\x1b[38;2;163;204;122mthings\x1b[39m\x1b[38;2;204;104;61m␍\x1b[39m\x1b[38;2;10;51;26m↵\x1b[39m\n\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m5\x1b[39m '),
	('Hope you are fine', '\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m7\x1b[39m '),
	('You are, right?', '\x1b[38;2;79;31;127m00\x1b[39m\x1b[38;2;255;63;178m8\x1b[39m '),
]

assert stylize_and_render_document(t, presets.fruity) == expected[0]

for n, (e_title, e_ansi) in zip(next(t.iter_nodes()).body.iter_nodes(), expected[1:]):
	assert n.title == e_title
	assert stylize_and_render_document(n.body, presets.fruity) == e_ansi

