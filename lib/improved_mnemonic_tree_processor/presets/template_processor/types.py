from .tokens import template_tokenizer
from .ast import switch, switch_branch, for_loop, execute, conditional, unconditional, indented, placeholder, sequence, template_tree, blank_line, render_template_by_name, meta_info, call_function

def template_sequence(seq):
	if len(seq) == 0:
		return None
	elif len(seq) == 1:
		return seq[0]
	else:
		return sequence(*seq)
