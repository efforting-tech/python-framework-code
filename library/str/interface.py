import re
from ..document.structures import Text_Match

class String_Interface:
	def regex_tokenize(self, token_patterns, start_pos=0):
		pattern_list = list()
		default_pattern = None

		if isinstance(token_patterns, dict):
			for key, pattern in token_patterns.items():
				if pattern is None:
					assert default_pattern is None
					default_pattern = key
				else:
					pattern_list.append((key, re.compile(pattern)))
		else:
			for index, pattern in enumerate(token_patterns):
				if pattern is None:
					assert default_pattern is None
					default_pattern = index
				else:
					pattern_list.append((index, re.compile(pattern)))

		#TODO - we should calculate the row indices - and we should make helpers for that (or maybe we let text_match do it if needed)
		pos = start_pos

		if isinstance(self, str):
			text = self
		else:
			text = self.to_str()

		best_candidate = True
		while best_candidate:
			best_candidate = None
			for key, pattern in pattern_list:
				if match := pattern.search(text, pos):
					pending_candidate = Text_Match(self, key, match)

					if best_candidate is None or (pending_candidate.match.start() < best_candidate.match.start()):
						best_candidate = pending_candidate
						if best_candidate.match.start() == pos:
							break

			if best_candidate:
				head = text[pos:best_candidate.match.start()]
				if head:
					if default_pattern:
						yield Text_Match(self, default_pattern, re.compile(r'.*', re.DOTALL).match(text[:best_candidate.match.start()], pos))	#Create unconditional match object by matching everything
					else:
						raise Exception()

				yield best_candidate
				pos = best_candidate.match.end()
				if best_candidate.match.start() == best_candidate.match.end():
					pos += 1	#Increment is required for when matching zero size


		tail = text[pos:]
		if tail:
			if default_pattern:
				yield Text_Match(self, default_pattern, re.compile(r'.*', re.DOTALL).match(text, pos))	#Create unconditional match object by matching everything
			else:
				raise Exception()

