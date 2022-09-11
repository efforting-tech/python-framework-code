import sys
from .runtime_utils import recursion_limit, forward_declared_instance, upgrade_forward_declared_item
from .iter_utils import iter_public_items, iter_public_values
from .filter_utils import dict_item_filter, item_filter
from . import conditions as C


CALLING_MODULE = forward_declared_instance()

class symbol:
	def __init__(self, name=None, bool_state=None, owner=CALLING_MODULE):
		self.name = name
		self.bool_state = bool_state

		if owner is CALLING_MODULE:
			self.owner = sys._getframe(1).f_globals['__name__']
		else:
			self.owner = owner

	def __get_state__(self):
		return self.name, self.bool_state, self.owner

	def __set_state__(self, state):
		self.name, self.bool_state, self.owner = state

	def __set_name__(self, target, name):
		assert self.name is None
		self.name = name

	def __bool__(self):
		if self.bool_state is not None:
			return self.bool_state
		else:
			return True

	def __repr__(self):
		try:
			with recursion_limit(1):
				if self.owner:
					return f'{self.owner}.{self.name}'
				else:
					return f'{self.name}'
		except RecursionError:
			return '…'

upgrade_forward_declared_item(CALLING_MODULE, symbol('CALLING_MODULE'))

class symbol_group_type(type):
	def __repr__(self):
		if self.__module__:
			return f'{self.__module__}.{self.__qualname__}'
		else:
			return f'{self.__qualname__}'

	def __dir__(self):
		items_of_symbol = item_filter(C.instance_of(symbol))
		yield from items_of_symbol(iter_public_values(self))


class symbol_group(metaclass=symbol_group_type):
	@classmethod
	def __init_subclass__(cls):
		items_of_symbol = dict_item_filter(value_condition=C.instance_of(symbol))
		for key, value in items_of_symbol(iter_public_items(cls)):
			value.owner = cls
