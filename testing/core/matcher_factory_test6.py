from efforting.mvp6._template_bootstrap_layer.processor import main
from efforting.mvp6._template_bootstrap_layer.context import template_implementation_context
from efforting.mvp6._template_bootstrap_layer.implementation import iteratively_implement_template
from efforting.mvp6.core.text import Immutable_Tree_View

r = main.dispatcher.dispatch_tree(Immutable_Tree_View.from_str('''

	This is a template.

	§ Note: This is a statement
		Part of statement

	§ This statement is «note: indirect»
		This is because it has expressions in its title
		But if we want «indirect» expressions inside the statement body the statement itself must support it.

	Here we have an «note: inline expression».
		Here is sub «note: stuff»!

'''))


ctx = template_implementation_context()
res = tuple(iteratively_implement_template(ctx, r.value))

