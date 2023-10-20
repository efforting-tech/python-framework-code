import sys
from pathlib import Path

from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_nodes import text_node
from ..symbols import register_symbol

from ..type_system.features import method_with_specified_settings, config_ro_access, get_settings, MISS, weak_and_lazy

from .context import context, reference
from . import actions as A
from . import matches as M

OK = register_symbol('internal.status.ok')

#TODO - move these to some sort of data harmonization module
#TODO - make sure to use some sort of namespace or enumeration so we can require coverage for the match statements in all these get-functions


class pending_action(public_base):
	processor = RTS.positional()
	rule = RTS.positional()
	config = RTS.positional()
	action = RTS.positional()
	match = RTS.positional()


#TODO - we should have a common rule system and maybe a common processor-API to harmonize things
class rule(public_base):
	condition = RTS.positional()
	action = RTS.positional(default=None)

	def check_match(self, item):
		return self.condition.check_match(item)

def call_bound_function_with_configuration_item_and_regex_match(bound_function, configuration_positionals, match):
	#The type_system.features.call_with_config is made for having multiple configurations as the final arguments but this
	#system will have them from the second positional instead.
	settings_name_list = tuple(bound_function.signature.parameters.keys())[1:1+len(bound_function.configuration.classes)]

	settings = dict()
	#unutilized_settings = set(updates)
	target = bound_function.instance or bound_function.owner


	assert len(configuration_positionals) >= len(settings_name_list)

	for settings_name, c, positional_config_ref in zip(settings_name_list, bound_function.configuration.classes, configuration_positionals):

		if c is RTS.SELF:
			c = bound_function.owner

		#This is not very pretty - it needs at least documentation and maybe then we can figure out a better way
		#TODO rework this entire thing - setup good testing

		cref = settings[settings_name] = config_ro_access(positional_config_ref._target)
		class_settings = cref._target


		for key, field in get_settings(c).items():
			if bound_function.instance and (settings_value := getattr(bound_function.instance, field.name, MISS)) is not MISS:
				existing = class_settings.get(key, MISS)
				if isinstance(existing, weak_and_lazy) or existing is MISS:	#If existing setting is not existing or weak, we override it
					class_settings[key] = settings_value
				else:	#Existing setting exists and is not weak
					class_settings[key] = existing

			elif (existing := class_settings.get(key, MISS)) is not MISS:	#for when there is no instance
				pass
			else:
				class_settings[key] = weak_and_lazy(field.get_or_create_default, target)


	regex_positionals, regex_named = get_match_as_arguments(match)
	return bound_function.function(target, config_ro_access(class_settings), match.item, *regex_positionals, **regex_named)

def call_bound_function_with_configuration_and_item(bound_function, configuration_positionals, match):
	#The type_system.features.call_with_config is made for having multiple configurations as the final arguments but this
	#system will have them from the second positional instead.
	settings_name_list = tuple(bound_function.signature.parameters.keys())[1:1+len(bound_function.configuration.classes)]

	settings = dict()
	#unutilized_settings = set(updates)
	target = bound_function.instance or bound_function.owner


	assert len(configuration_positionals) >= len(settings_name_list)

	for settings_name, c, positional_config_ref in zip(settings_name_list, bound_function.configuration.classes, configuration_positionals):

		if c is RTS.SELF:
			c = bound_function.owner

		#This is not very pretty - it needs at least documentation and maybe then we can figure out a better way
		#TODO rework this entire thing - setup good testing

		cref = settings[settings_name] = config_ro_access(positional_config_ref._target)
		class_settings = cref._target


		for key, field in get_settings(c).items():
			if bound_function.instance and (settings_value := getattr(bound_function.instance, field.name, MISS)) is not MISS:
				existing = class_settings.get(key, MISS)
				if isinstance(existing, weak_and_lazy) or existing is MISS:	#If existing setting is not existing or weak, we override it
					class_settings[key] = settings_value
				else:	#Existing setting exists and is not weak
					class_settings[key] = existing

			elif (existing := class_settings.get(key, MISS)) is not MISS:	#for when there is no instance
				pass
			else:
				class_settings[key] = weak_and_lazy(field.get_or_create_default, target)


	return bound_function.function(target, config_ro_access(class_settings), match.item)




def process_positionals(processors, positional):
	i = iter(positional)
	return (*(p(a) for p, a in zip(processors, i)), *i)

def process_named(processors, named):
	result = dict(named)
	for n, p in processors.items():
		result[n] = p(named[n])

	return result

def resolve(item):
	return item		#For now we will skip the resolution since we may want to be able to use references in context parents


	# #TODO - decide if this should be deep or not
	# match item:
	# 	case reference(target):
	# 		return target
	# 	case _:
	# 		return item

def resolve_positionals(positional):
	return tuple(map(resolve, positional))

def resolve_named(named):
	return {k: resolve(v) for k, v in named.items()}



def get_match_as_arguments(item):
	match item:
		case M.matched_condition(match=match):
			return get_match_as_arguments(match)

		case M.matched_regex():
			return item.as_arguments

		case M.matched_value() | M.matched_unconditionally():
			return ((), {})

		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')


def get_node_body(item):
	match item:
		case text_node():
			return item.body

		case M.matched_condition(item=sub_item):
			return get_node_body(sub_item)


		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')


def get_context(item):
	match item:
		case context():
			return item

		case reference(target):
			return get_context(target)

		case _ as unhandled:
			raise Exception(f'The value {unhandled!r} could not be handled')


class improved_text_node_processor(public_base):
	rules = RTS.optional_factory(list)
	context = RTS.setting(factory=context.from_this_frame, factory_positionals=(3,), factory_named=dict(name='default_context'))	#Why 3? Will it change? Is this a terrible practice?
	default_action = RTS.setting(None)
	name = RTS.setting(None)		#Should possibly not be config though
	include_blanks = RTS.setting(False)
	workdir = RTS.setting(None)

	def add_rule(self, condition, action):
		self.rules.append(rule(condition, action))



	#Maybe the action processor should be a whole own module - then we could also have one built in and one that can be extended
	@method_with_specified_settings(RTS.SELF)
	def process_action(self, action, match, *, config):
		match action:
			case A.return_value(value):
				return value

			case A.return_processed_match(processor):
				return processor(match)

			case A.execute_node_body_in_context(context):
				get_context(context).exec(get_node_body(match).text)
				return OK

			case A.call_function_using_regex_match_as_arguments(function):
				positional, named = get_match_as_arguments(match)

				positional = process_positionals(action.positional_processors, positional)
				named = process_named(action.named_processors, named)

				positional += resolve_positionals(action.additional_positional)
				named.update(resolve_named(action.additional_named))

				return function(*positional, **named)

			case A.call_function_with_regex_match(function):
				positional = (get_match_as_arguments(match),)
				positional += resolve_positionals(action.additional_positional)

				return function(*positional, **action.additional_named)

			case A.call_function_with_processor_node_and_regex_match(function):
				positional = (get_match_as_arguments(match),)
				positional += resolve_positionals(action.additional_positional)

				return function(self, match.item, *positional, **action.additional_named)

			case A.call_function_with_config_processor_node_and_regex_match(function):
				positional = (get_match_as_arguments(match),)
				positional += resolve_positionals(action.additional_positional)

				return function(config, self, match.item, *positional, **action.additional_named)

			case A.call_function_with_node_and_regex_args(function):
				positional, named = get_match_as_arguments(match)
				positional = (config.context, match.item, *positional, *resolve_positionals(action.additional_positional))
				named.update(resolve_named(action.additional_named))

				return function(*positional, **named)


			case A.bind_and_call_function_with_processor_config_and_regex_args(function):
				return call_bound_function_with_configuration_item_and_regex_match(function.__get__(self, self.__class__), (config,), match)

			case _ if action is A.return_match:
				return match

			case _ if action in A.TRANSPARENT_ACTION_SET:
				return action

			case _ as unhandled:
				raise Exception(f'The value {unhandled!r} could not be handled')

	@method_with_specified_settings(RTS.SELF)
	def process_tree_iteratively(self, tree, *, config):
		for node in tree.iter_nodes(include_blanks=config.include_blanks):
			yield self.process_node.call_with_config(config, node)

	@method_with_specified_settings(RTS.SELF)
	def process_node(self, node, *, config):
		for rule in self.rules:
			if match := rule.check_match(node):
				return self.process_action.call_with_config(config, rule.action, match)

		if self.default_action:
			return self.process_action.call_with_config(config, self.default_action, M.matched_unconditionally(node))

		raise Exception(f'The node {node.title!r} could not be handled by {self}')


	@method_with_specified_settings(RTS.SELF)
	def process_tree(self, tree, *, config):
		return tuple(self.process_tree_iteratively.call_with_config(config, tree))

	@method_with_specified_settings(RTS.SELF)
	def process_text(self, text, *, config):
		tree = text_node.from_text(text)
		return tuple(self.process_tree_iteratively.call_with_config(config, tree))

	@method_with_specified_settings(RTS.SELF)
	def process_path(self, filename, *, config):
		target_file = Path(config.workdir or '.') / filename
		tree = text_node.from_path(target_file)
		return tuple(self.process_tree_iteratively.call_with_config(config, tree))





	@method_with_specified_settings(RTS.SELF)
	def resolve_tree_iteratively(self, tree, *, config):
		for node in tree.iter_nodes(include_blanks=config.include_blanks):
			yield self.resolve_node.call_with_config(config, node)

	@method_with_specified_settings(RTS.SELF)
	def resolve_node(self, node, *, config):
		for rule in self.rules:
			if match := rule.check_match(node):
				return pending_action(self, rule, config, rule.action, match)

		if self.default_action:
			return pending_action(self, rule, config, self.default_action, M.matched_unconditionally(node))

		raise Exception(f'The node {node.title!r} could not be handled by {self}')


	@method_with_specified_settings(RTS.SELF)
	def resolve_tree(self, tree, *, config):
		return tuple(self.resolve_tree_iteratively.call_with_config(config, tree))

	@method_with_specified_settings(RTS.SELF)
	def resolve_text(self, text, *, config):
		tree = text_node.from_text(text)
		return tuple(self.resolve_tree_iteratively.call_with_config(config, tree))

	@method_with_specified_settings(RTS.SELF)
	def resolve_path(self, filename, *, config):
		target_file = Path(config.workdir or '.') / filename
		tree = text_node.from_path(target_file)
		return tuple(self.resolve_tree_iteratively.call_with_config(config, tree))


	def __repr__(self):	#This is a common repr, we should reuse it
		if self.name:
			return f'{self.__class__.__qualname__}({self.name!r})'
		else:
			return f'{self.__class__.__qualname__}({hex(id(self))})'


