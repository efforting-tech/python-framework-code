from ...record.base.public import Structure
from ...record import member as M
from ...iteration import Switchable_Iterator
from ... import ABC

class Token_Stream(Switchable_Iterator):
	text = M.positional(None)
	pending_position = M.positional(0)


@ABC.Action
class Enter_Sub_Parser(Structure):
	sub_parser = M.positional()
