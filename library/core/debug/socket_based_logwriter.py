import socket
ANSI_CLEAR = b'\033[H\033[2J\033[3J'

class Indented_Socket_Log_Writer:
	def __init__(self, host, port):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((host, port))
		self.pending_clear = True
		self._current_indent = ''

	def clear(self):
		self.socket.sendall(ANSI_CLEAR)

	def print(self, *pieces, end='\n', flush=False):	#Note - flush is ignored, just for API compatibility with print
		if self.pending_clear:
			self.clear()
			self.pending_clear = False

		final = ' '.join(map(str, pieces)) + end
		for sub_line in final.splitlines(keepends=True):
			self.socket.sendall((self._current_indent + sub_line).encode('utf-8'))

	def indent(self, indent='    '):
		return Indented_Socket_Log_Writer_Context_Manager(self, indent)


class Indented_Socket_Log_Writer_Context_Manager:
	def __init__(self, log_writer, indent):
		self.log_writer = log_writer
		self.indent = indent

	def __enter__(self):
		self.log_writer._current_indent += self.indent
		return self.log_writer

	def __exit__(self, et, ev, tb):
		self.log_writer._current_indent = self.log_writer._current_indent[:-len(self.indent)]


# #DEMO

# log = Indented_Socket_Log_Writer('localhost', 5001)

# log.print('Hello!')
# with log.indent():
# 	log.print('World')
# 	with log.indent('    BLARGH> '):
# 		log.print('and stuff')
# 	log.print('---')
# log.print('!!!')

# # $ nc -lkp 5001   # netbsd version of nc
# # Hello!
# #     World
# #         BLARGH> and stuff
# #     ---
# # !!!