from ..type_system.bases import public_base
from .. import type_system as RTS
import os


#NOTE - replace this with contextlib.chdir when python 3.11 is out
class workdir(public_base):
	target = RTS.positional()
	previous = RTS.field(factory=list)

	def __enter__(self):
		self.previous.append(os.getcwd())
		os.chdir(self.target)

	def __exit__(self, et, ev, tb):
		os.chdir(self.previous.pop(-1))
