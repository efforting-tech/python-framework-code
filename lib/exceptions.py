from .pre_rts import pre_rts_type
import types


class DataConversionFailed(pre_rts_type, ValueError):
	#TODO - compare notes with rts_types for doc?
	_default_values = dict(
		abc_type =							None,
		value =								None,
	)

	def __str__(self):
		return f'{self.__class__.__qualname__}: No conversation found using {self.abc_type.symbol} for data of type {type(self.value)}.'



class TokenizationFailed(pre_rts_type, ValueError):	#NOTE this is an abstract exception (TODO mark it as such)
	_default_values = dict(
		tokenizer =			None,
		text = 				None,
		start = 			None,
		level = 			None,
		config = 			None,
		match = 			None,
	)


class TokenizationUnhandledAction(TokenizationFailed):
	def __str__(self):
		return f'{self.__class__.__qualname__}: No action was found for {self.match} in tokenizer {self.tokenizer}.'
