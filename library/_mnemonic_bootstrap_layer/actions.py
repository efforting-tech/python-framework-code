from ..core import record as R
from ..symbol_factory import Local_Symbol

class Store_Node_As(R.Record):
	name: R.Field()
	processor: R.Field() = None

class Store_Text_As(R.Record):
	name: R.Field()

Requires_Empty = Local_Symbol('Requires_Empty')

