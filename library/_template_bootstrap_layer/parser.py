from .tokenizer import template_tokenizer

def parse_line(line, source=None):
	result = template_tokenizer.tokenize(line, source=source)
	return result.tokens

