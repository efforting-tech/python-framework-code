from .. import Symbol as S
from ..core import record as R
from ..core.symbol import Enum as E

class Include(R.Record):
	path: R.Field()

class Emit(R.Record):
	path: R.Field()

class Tree(R.Record):
	title: R.Field()
	body: R.Field()

Well_Known = E('Well_Known',
	'Current_Function',
)

