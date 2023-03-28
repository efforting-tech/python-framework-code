from .function_utils.create_function import simple_dynamic_initializer	 #TODO - probably don't use this here (also check with testing system)
import types

#TODO - pretty sure we made a better "simple type" we could use here


class DataConversionFailed(ValueError):
	#TODO - compare notes with rts_types for doc?
	_default_values = dict(
		abc_type =							None,
		value =								None,
	)

	__init__ = simple_dynamic_initializer(_default_values)

	def __str__(self):
		return f'No conversation found using {self.abc_type.symbol} for data of type {type(self.value)}.'

