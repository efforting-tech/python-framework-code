from .... import type_system as RTS
from ....type_system.bases import public_base
from ....symbols import create_symbol



blank_line = create_symbol('template.blank_line')

class switch(public_base):
	expression = RTS.positional()
	branches = RTS.factory(list)

class switch_branch(public_base):
	test = RTS.positional()
	sub_template = RTS.positional()

class render_template_by_name(public_base):
	name = RTS.positional()

class for_loop(public_base):
	expression = RTS.positional()
	sub_template = RTS.positional()

# class call_function(public_base):
# 	function = RTS.positional()
# 	positional = RTS.all_positional()
# 	named = RTS.all_named()

class execute(public_base):
	code = RTS.positional()

class call_function(public_base):
	function = RTS.positional()
	signature = RTS.positional()

class conditional(public_base):
	test = RTS.positional()
	sub_template = RTS.positional()
	chain = RTS.positional(default=None)

	def append_chain(self, chain):
		if self.chain is None:
			self.chain = chain
		else:
			self.chain.append_chain(chain)

class unconditional(public_base):
	sub_template = RTS.positional()

class indented(public_base):
	sub_template = RTS.positional()

class placeholder(public_base):
	name = RTS.positional()

	@classmethod
	def from_match(cls, match):
		return cls(match.group(1).strip())

class sequence(public_base):
	sequence = RTS.all_positional()

class meta_info(public_base):
	body = RTS.positional()
	name = RTS.positional(default=None)
	signature = RTS.positional(default=())

class template_tree(public_base):
	title = RTS.positional(default=None)
	children = RTS.positional(factory=list)
