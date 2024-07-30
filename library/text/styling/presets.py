from ..styling import Style_Manager, Event, Filter, HSV

def format_cc(text):
	result = ''
	for c in text:
		o = ord(c)
		if o >= 0 and o <= 0x20:
			result += chr(0x2400 + ord(c))
		else:
			result += repr(c)[1:-1]

	return result



default = Style_Manager()

default.define_style('row-leading-zeros',
	(Event.push('background_color', 'red'), Event.push('foreground_color', 'dark-red')),
	(Event.pop('background_color'), Event.pop('foreground_color')),
)

default.define_style('row-value',
	(Event.push('background_color', 'red'), Event.push('foreground_color', 'white'),),
	(Event.pop('background_color'), Event.pop('foreground_color'),),
)

default.define_style('highlight',
	(Event.push('invert', True), Event.push('background_color', 'magenta')),
	(Event.pop('background_color'), Event.pop('invert'),),
)

default.define_style('text',
	(Event.push('foreground_color', 'grey'),),
	(Event.pop('foreground_color'),),
)

default.define_style('mnemonic',
	(Event.push('foreground_color', 'green'),),
	(Event.pop('foreground_color'),),
)

default.define_style('white-space',
	(Event.push('foreground_color', 'brown'),),
	(Event.pop('foreground_color'),),
)

default.define_style('control-character',
	(Event.push('foreground_color', 'cyan'), Event.push('italics', 'True'), Event.push('filters', Filter.function(format_cc))),
	(Event.pop('foreground_color'), Event.pop('italics'), Event.pop('filters')),
)

default.define_style('punctuation',
	(Event.push('foreground_color', 'brown'),),
	(Event.pop('foreground_color'),),
)

default.define_style('expression',
	(Event.push('foreground_color', 'magenta'), Event.push('italics', 'True'),),
	(Event.pop('foreground_color'), Event.pop('italics'),),
)

fruity = Style_Manager()

fruity.define_style('row-leading-zeros',
	(Event.push('foreground_color', HSV(0.75, 0.75, .5)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('row-value',
	(Event.push('foreground_color', HSV(0.9, 0.75, 1)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('text',
	(Event.push('foreground_color', HSV(0.25, 0.4, 0.8)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('mnemonic',
	(Event.push('foreground_color', HSV(0.37, 0.7, 0.8)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('highlight',
	(Event.push('underline', True), Event.push('bold', True)),
	(Event.pop('underline'), Event.pop('bold')),
)

fruity.define_style('white-space',
	(Event.push('foreground_color', HSV(0.4, 0.8, 0.2)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('control-character',
	(Event.push('foreground_color', HSV(0.05, 0.7, 0.8)), Event.push('filters', Filter.function(format_cc)),),
	(Event.pop('foreground_color'), Event.pop('filters'),),
)

fruity.define_style('punctuation',
	(Event.push('foreground_color', HSV(0.7, 0.5, 0.8)),),
	(Event.pop('foreground_color'),),
)

fruity.define_style('expression',
	(Event.push('foreground_color', HSV(0.55, 0.6, 0.9)), Event.push('italics', True)),
	(Event.pop('foreground_color'), Event.pop('italics')),
)

