from .._mnemonic_bootstrap_layer import create_records

F_AST = create_records('''

	abstract_node: source
		text: content

		abstract_tree: title, body
			node
			statement

		inline_expression: expression

''', 'F_AST')


CS_AST = create_records('''

	ast_node: source
		abstract_multiline_text: title, body
			note
			inline_note

		define_pythonic_inline_expression: pattern, body

		unresolved_inline_expression: expression
		custom_inline_expression: function, parameters

''', 'CS_AST')


N_AST = create_records('''

	ast_node: source
		abstract_tree: title, body
			node
			indirect_statement

''', 'N_AST')


