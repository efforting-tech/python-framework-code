from ..matching import data_condition as DC
from .. import symbol
from ..document import structures as DS

T = symbol.text.token



#Helpers
def literal_token_equality(token, value=None):
	if value is not None:
		return DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(token), match=DC.Structure_Match(group=DC.Call_And_Compare_Return_Value(DC.Equality(value))))
	else:
		return DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(token))

def word(value=None):
	return literal_token_equality(T.word, value)

def literal(value=None):
	return literal_token_equality(T.literal, value)

def optional(*sub_items):
	return DC.Sequence(*sub_items) | DC.Always_True

def join_sequence(separator, *sequence, expand_sub_sequences=True, require_sequence_type=None):
	#NOTE  that expand_sub_sequences does not insert separators, which is the idea of it.
	#		to do it differently, just call this function with an already expanded sequence
	NO_ITEM = object()	#TODO - local symbol
	last_item = NO_ITEM
	result = DC.Sequence()
	for item in sequence:
		if last_item is not NO_ITEM:
			result.append(separator)

		if expand_sub_sequences and type(item) in (tuple, list):	#Note that we require pure tuple or list, not descendents
			result.extend(item)
		else:
			result.append(item)
		last_item = item

	if require_sequence_type:
		return DC.Type_Instance(require_sequence_type) & result
	else:
		return result

ws = DC.Type_Instance(DS.Text_Match) & DC.Structure_Match(token=DC.Identity(T.whitespace))
