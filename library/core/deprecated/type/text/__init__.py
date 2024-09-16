from ...interface.text.tree import Immutable_Text_Tree_Interface
from ...state.text import Immutable_Line_View_State


class Immutable_Line(Immutable_Line_View_State, Immutable_Text_Tree_Interface):
	pass

class Immutable_Text_Tree(Immutable_Line_View_State, Immutable_Text_Tree_Interface):
	pass