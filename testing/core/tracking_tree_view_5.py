from efforting.mvp6 import ABC
from efforting.mvp6.core import record as R
from efforting.mvp6.core.dispatcher.rules import Unconditional_Rule, Core_Rule, Regex_Rule, Tree_View_Regex_Rule, Node_Classification_Rule
from efforting.mvp6.core.dispatcher.tree_view import Tree_View_Dispatcher
from efforting.mvp6.core.text.tree import Tree_Node, Tree_Node_Classification
from tracking_tree_view_2 import render_non_printables

import re
import textwrap

from efforting.mvp6._mnemonic_bootstrap_layer.expression_parser import translate_tokens_to_regex
from efforting.mvp6._template_bootstrap_layer.records import F_AST





# root = Tree_Node.from_str('''
# 		Hello World!
# 			This is a test

# 	Here is another node
# 		With another body


# 	Here is even more
# 		freakin nodes
# 		and such!

# ''')

# tvd = Tree_View_Dispatcher()
# @tvd.register(Tree_View_Regex_Rule, re.compile('^Here is(.*)'))
# def func(context, dispatcher, node, result):
# 	print(f'We found yet {result.value.match.group(1).strip()} with {node.count_body_nodes()} sub nodes.')
# 	if node.body:
# 		print('Here are the sub nodes:')
# 		for s in node.body.iter_nodes():
# 			print(repr(s.to_str()))
# 			#print(textwrap.indent(render_non_printables(s.to_str()), '  '))



# @tvd.register(Node_Classification_Rule, {
# 	Tree_Node_Classification.Malformed_Tree,
# 	Tree_Node_Classification.Malformed_Node,
#  })
# def dfunc(context, dispatcher, node, result):
# 	print(f'Warning - skipping malformed node: {node}')



# tvd.bound_dispatch_tree('context', root)
