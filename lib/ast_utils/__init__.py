import ast

def parse_expression(text):
	[expr] = ast.parse(text).body
	return expr.value

def parse_statement(text):
	[statement] = ast.parse(text).body
	return statement
