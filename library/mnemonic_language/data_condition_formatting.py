from ..processing.generic import Type_LUT_Processor
from ..matching import data_condition as DC
from ..symbol_factory import Symbol
import types

dc_formatter = Type_LUT_Processor('dc_formatter')


def maybe_parenthesis(text):
	if ' ' in text:
		return f'({text})'
	else:
		return text


@dc_formatter.register(tuple)
def format_tuple(processor, item):
	inner = ', '.join(map(processor.process_item, item))
	return f'[{inner}]'

@dc_formatter.register(DC.Sequence)
def format_tuple(processor, item):
	inner = ', '.join(map(processor.process_item, item))
	return f'Sequence({inner})'

@dc_formatter.register(DC.All)
def format_tuple(processor, item):
	return ' & '.join(map(maybe_parenthesis, map(processor.process_item, item)))

@dc_formatter.register(DC.Type_Instance)
def format_tuple(processor, item):
	return f'instance of {maybe_parenthesis(processor.process_item(item.value))}'

@dc_formatter.register(DC.Identity)
def format_tuple(processor, item):
	return f'is {maybe_parenthesis(processor.process_item(item.value))}'

@dc_formatter.register(DC.Equality)
def format_tuple(processor, item):
	return f'= {maybe_parenthesis(processor.process_item(item.value))}'

@dc_formatter.register(DC.Capture)
def format_tuple(processor, item):
	return f'as {item.name}'

@dc_formatter.register(DC.Wrap_Capture)
def format_tuple(processor, item):
	return f'wrap capture {item.capture!r} using {maybe_parenthesis(processor.process_item(item.wrapper))}'

@dc_formatter.register(DC.Structure_Match)
def format_tuple(processor, item):
	inner = ', '.join(f'{name}: {processor.process_item(sub_item)}' for name, sub_item in item.value.items())
	return f'structure({inner})'

@dc_formatter.register(DC.Call_And_Compare_Return_Value)
def format_tuple(processor, item):
	return f'return of calling {processor.process_item(item.value)}'






@dc_formatter.register(type)
@dc_formatter.register(types.FunctionType)
def format_tuple(processor, item):
	return f'<{item.__qualname__}>'



@dc_formatter.register_default()
def format_tuple(processor, item):
	return repr(item)
