from ..context import context
from ..processing.text_tree import Mnemonic_Text_Tree_Processor, Text_Tree_Processor_State
from ..processing.generic import Type_LUT_Processor
from ..processing.structures import Processor_State

from .utilities import register_mnemonic_function, get_mnemonic, tokenize_text, register_mnemonic_record

from ..matching import data_condition as DC
from .. import symbol

from ..record import member as M
from ..record.base.public import Structure

from ..document import create_text_tree_document_from_path
from ..resources import get_resource_path


#NEXT UP - make processors accessible, we could identity them by symbols or names


#NEXT UP - make mnemonic function be able to call using modified context


#NEXT UP - Figure out how we want to deal with captures an aliases.
#			if we for instance were to pop a capture by name we must be sure of that name
#			another solution might be if we push the captures to a local symbol and then pop it, then we know exactly what is in it.
#			I think a good first solution is that we push and pop by name and that we get the name using the cfit of sub_captures

#NEXT UP - context_manipulation - one issue now is we need to do comma separated pattern, we should figure that out (a repeating or recursing branch might work?)

#TODO - we keep having to wrap thigns as Mnemonic and Expression, maybe we should relax that a bit to make it easier to compose new patterns babsed on existing processors since that is the more common use case.


mnemonic_language_processor = Mnemonic_Text_Tree_Processor('mnemonic_language_processor')
amend_definition_processor = Mnemonic_Text_Tree_Processor('amend_definition_processor')
#processor_setup_processor = Mnemonic_Text_Tree_Processor('processor_setup_processor')
context_manipulation_processor = Mnemonic_Text_Tree_Processor('context_manipulation_processor')

from .structures import Mnemonic, pending_function_with_advanced_unwrapper, pending_mnemonic_implementation, context_manipulation



from .mnemonic_tokens_to_pattern import mlexp, mttpex, mttp
from .parser import tp
from .string_formatting_rules import string_formatter
from .rudimentary_definition_helpers import word, literal, ws
from .mnemonic_captures import cfit
#from .parsing_rules import compare_mnemonic_items
from .structures import Expression



#TODO - move this whole thing out
class pattern_state(Processor_State):
	rename_from = M.positional()
	rename_to = M.positional()

pattern_renamer = Type_LUT_Processor('pattern_renamer', STATE_TYPE = pattern_state)

@pattern_renamer.register(DC.All)
@pattern_renamer.register(DC.Any)
@pattern_renamer.register(DC.Sequence)
def rename_pattern(processor, pattern):
	for sub_pattern in pattern:
		processor.process_item(sub_pattern)

@pattern_renamer.register(DC.Type_Instance)
@pattern_renamer.register(DC.Identity)
def rename_pattern(processor, pattern):
	pass

@pattern_renamer.register(DC.Structure_Match)
def rename_pattern(processor, pattern):
	for name, sub_expected in pattern.value.items():
		processor.process_item(sub_expected)


@pattern_renamer.register(DC.Capture)
@pattern_renamer.register(DC.Capture_Remaining)
def rename_pattern(processor, pattern):
	if processor.rename_from == pattern.name:
		pattern.name = processor.rename_to

@pattern_renamer.register(DC.Wrap_Capture)
def rename_pattern(processor, pattern):
	if processor.rename_from == pattern.capture:
		pattern.capture = processor.rename_to


# @register_mnemonic_function(mlexp, mttpex.process_item(tp.process_text('alias')))	#TODO - make another decorator for this purpose
# def alias(processor_state):
# 	return word() & DC.Capture('alias') & DC.Wrap_Capture('alias', lambda n: string_formatter().process_item(n))

@register_mnemonic_function(mlexp, mttpex.process_item(tp.process_text('{pattern} as {name}')))
def capture_as_alias(processor_state, pattern, name):
	#TODO - determine - Here we convert to Expression in order to match it using mlexp but perhaps mlexp should not care about that as long as it is a sequence?
	pending_pattern = mlexp().process_item(Expression(*pattern))
	#sub_captures = tuple(cfit(pending_pattern))
	[(capt, capt_name)] = cfit(pending_pattern)

	#print(getattr(capt ,capt_name), '→', name, pending_pattern)

	#TODO - this is a mess! First I was thinking it might be easier to use a push/pop method to capture the original pattern and then transfer to name
	#		but now I am thinking that perhaps we should just have features for renaming a capture in a pattern

	pattern_renamer(state=dict(rename_from=getattr(capt ,capt_name), rename_to=name)).process_item(pending_pattern)
	return pending_pattern


	#TODO - we will pop all sub captures and store as a new capture - but this should be done in a way that doesn't conflict with any pending patterns
	#		possibly this could be done by using some identity instance instead of str for temporary capture names
	#HACK - for now we will assume a single capture and rename it
	#BUG - when we do this renaming, we aren't renaming processing steps causing issues
	#		A better solution is to push and pop captures so we can pop the captures after it has been processed and push it as the alias





	#exit()

	#setattr(capt, capt_name, name)

	#temp_name = object()	#Just some local identity
	# return DC.Pop_And_Push_Capture(capt_name, temp_name) & (
	# 	(pending_pattern & DC.Pop_And_Push_Capture(temp_name, name)) |		#Transfer temp_name to new name if we match
	# 	DC.Pop_And_Push_Capture(temp_name, capt_name)		#Restore capture if we don't match
	# )


	# return DC.Pop_And_Push_Capture(capt_name, temp_name) & (	#Push existing name to temp_name
	# 	pending_pattern 	#match pending pattern into existing name
	# 	& DC.Pop_And_Push_Capture(capt_name, name)	#move existing name to new name (alias)
	# 	& DC.Pop_And_Push_Capture(temp_name, capt_name)	#Restore temp name to existing name
	# ) | DC.Pop_And_Push_Capture(temp_name, capt_name)	#Restore temp name to existing name

	#return word() & DC.Capture('alias') & DC.Wrap_Capture('alias', lambda n: string_formatter().process_item(n))


register_mnemonic_record(context_manipulation_processor, 'new context')(lambda : symbol.mnemonic.context.manipulation.new_context)	#TODO - make nicer ways to return values, records and calling functions
register_mnemonic_record(context_manipulation_processor, '-{name}')(context_manipulation.exclude)
#register_mnemonic_record(context_manipulation_processor, '{text as uri} as {name as alias}')(context_manipulation.include)
register_mnemonic_record(context_manipulation_processor, '{text as uri}')(context_manipulation.include)



from ..document import create_text_tree_document_from_str
print(context_manipulation_processor().process_node(create_text_tree_document_from_str('stuff as things')))

exit()

# print(mlexp().process_item(Expression(*tp.process_text('pattern as thing'))))
# #print(get_mnemonic('{stuff as alias}'))

# exit()


# from .parsing_rules import element_comparator
# #t = tokenize_text('-hello')
# #p = get_mnemonic('-{name}') & DC.Update_Flag('flags', symbol.mnemonic.context.manipulation.discard_entry)



# def test_func(name, alias):
# 	return dict(type='alias', name=name, alias=alias)

# t = tokenize_text('thing as stuff')
# p = DC.Branch(
# 	get_mnemonic('{name} as {alias}') & DC.Call_Function('name', test_func, positional_captures=('name', 'alias')),			#TODO NEXT UP!!
# 	#get_mnemonic('+{name}') & DC.Wrap_Capture('name', str.upper),
# 	#get_mnemonic('-{name}') & DC.Wrap_Capture('name', str.lower)
# )



# #t = tokenize_text('hello as thing')
# #p = get_mnemonic('{name} as {alias}') & DC.Update_Flag('flags', symbol.mnemonic.context.manipulation.discard_entry)

# ec = element_comparator()
# print(ec.compare_items(p, t))
# print(ec.captures)


# exit()

# print(
# 	get_mnemonic('-{name}') | get_mnemonic('+{name}') | get_mnemonic('-{name}')
# )










	#TODO - create and use register_mnemonic_record
	# @register_mnemonic_function(context_manipulation_processor, '{name} as {name as alias}')
	# def name_as_alias(processor_state, name, alias):
	# 	return('name_as_alias', name,  alias)

	# @register_mnemonic_function(context_manipulation_processor, '-{name}')
	# def name_exclude(processor_state, name):
	# 	return('name_exclude', name)

	# @register_mnemonic_function(context_manipulation_processor, '{name}')
	# def name_include(processor_state, name):
	# 	return('name_include', name)



#class setup_processor:
	# @register_mnemonic_function(processor_setup_processor, 'CTX[:] {pattern}')
	# def mnemonic_function(processor_state, pattern):
	# 	print('CTX', pattern)


	# @register_mnemonic_function(processor_setup_processor, '{name as tag}[:] {pattern}')
	# def mnemonic_function(processor_state, tag, pattern):
	# 	#BUG (Design error) - If we want a repeating pattern we must be able to do partial matching - this means we should use API similar to string `search´, `match´ and `fullmatch´
	# 	#TODO - here we assume r.condition is mnemonic and get .value, we should probably do this in a better way
	# 	#NOTE 'rule' could just as well be a symbol, possibly a local one
	# 	csp = DC.Repeat(DC.Branch(DC.Sequence(literal(',') | ws), *(r.condition.value & DC.Set_Capture('rule', r) & DC.Push_Capture_State('items') for r in context_manipulation_processor.rules)))
	# 	c = element_comparator()
	# 	c.compare_items(csp, Mnemonic(*pattern))

	# 	pmi = processor_state.context.require('pending_mnemonic_implementation')
	# 	#TODO - we must document how this works - it is a bit messy
	# 	for sub_item in c.captures['items']:
	# 		ps = Text_Tree_Processor_State(context_manipulation_processor, captures=sub_item)

	# 		mutation = ps.process_action(sub_item['rule'].action)
	# 		mutation.tag = tag	#TODO - Translate to symbol
	# 		pmi.context_setup.append(mutation)

	# 		print('MUT', mutation)





#TODO - we should have a common one that is included in the other ones instead of explicitly adding this to every one
@register_mnemonic_function(mnemonic_language_processor, '#{pattern}')
@register_mnemonic_function(amend_definition_processor, '#{pattern}')
#@register_mnemonic_function(processor_setup_processor, '#{pattern}')
@register_mnemonic_function(context_manipulation_processor, '#{pattern}')
def ignore_comment(processor_state, pattern):
	pass


class amend_processor:

	@register_mnemonic_function(mnemonic_language_processor, 'amend current processor[:]')
	def amend_current_processor(processor_state):
		#TODO we should improve api so we can make a new state while doing adjustments
		ps = processor_state.with_processor(amend_definition_processor)

		ps.context = ps.context.sub_context(dict(
			target_processor=processor_state,
			pending_mnemonic_implementation = pending_mnemonic_implementation(),
		))
		ps.process_tree(processor_state.node.body)


	@register_mnemonic_function(amend_definition_processor, 'setup[:]')
	def setup(processor_state):
		#ps = processor_state.with_processor(processor_setup_processor)
		#ps.process_tree(processor_state.node.body)

		mutation_list = processor_state.with_processor(context_manipulation_processor).process_tree(processor_state.node.body)

		processor_state.context.require('pending_mnemonic_implementation').context_setup.extend(mutation_list)


	@register_mnemonic_function(amend_definition_processor, 'mnemonic function[:] {pattern}')
	def mnemonic_function(processor_state, pattern):
		target_processor = processor_state.context.require('target_processor')
		pending_mnemonic_implementation = processor_state.context.require('pending_mnemonic_implementation').copy() #We copy so we get current state
		register_mnemonic_function(target_processor, pattern, pending_function_with_advanced_unwrapper(processor_state.node.body, pending_mnemonic_implementation))





processor_registry = dict()

root_context = context('root', dict(
	#...
))


mlp = mnemonic_language_processor(state=dict(context=root_context))
boot_tree = create_text_tree_document_from_path(get_resource_path('mnemonic_language_bootstrap.tdef'))
mlp.process_tree(boot_tree)