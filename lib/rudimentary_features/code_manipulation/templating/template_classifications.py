from ....symbols import register_symbol


class CL:
	token = register_symbol('internal.templating.token')

	expression = token()
	text = token()
