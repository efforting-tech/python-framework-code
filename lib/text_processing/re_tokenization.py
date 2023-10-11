import re

#IMPORTANT TODO - we should harmonize the re_tokenization and tokenization stuff to be compatible with PM
from ..symbols import register_multiple_symbols

UNMATCHED, RAISE_EXCEPTION, SKIP = register_multiple_symbols(*'internal.unmatched internal.action.raise_exception internal.skip'.split())	#TODO allow any old string


hacky_pattern = re.compile('.*', re.S)	#This is because we can't create match objects ourselves
def unconditional_match(text, start=0, end=None):
	return hacky_pattern.match(text[:end], start)

def literal_re_pattern(x):
	return re.compile(re.escape(x))


def re_tokenize(text, matchers, start=0, include_unmatched=True, unmatched=UNMATCHED):
	pos = start

	while pos <= len(text):

		pending_best_match = None
		for pattern, action in matchers:
			if match := pattern.search(text, pos):
				if pending_best_match is None or match.start() < pending_best_match.start():
					pending_best_match = match
					pending_best_action = action

					if match.start() == pos:	#early bail
						break
		if pending_best_match:

			head = unconditional_match(text, pos, pending_best_match.start())
			assert head.group() == text[pos:pending_best_match.start()]

			if head.group() and include_unmatched:
				if unmatched is RAISE_EXCEPTION:
					raise Exception(f'Unexpected head: {head.group()!r}')
				yield unmatched, head

			if pending_best_action is not SKIP:
				yield pending_best_action, pending_best_match

			if pos == pending_best_match.end():	#Advance one position for null sized matches
				pos += 1
			else:
				pos = pending_best_match.end()
		else:
			tail = unconditional_match(text, pos)
			if tail.group() and include_unmatched:
				if unmatched is RAISE_EXCEPTION:
					raise Exception(f'Unexpected tail: {tail.group()!r}')
				yield unmatched, tail

			break