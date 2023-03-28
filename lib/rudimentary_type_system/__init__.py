#Maybe this needs to be moved as well so we can access the pre_rts stuff without going by here
if False:
	from .rts_types import field, field_configuration, SELF, initializer, SETTING, replace_initializer
	from .caching import cached_property
	from . import initialization, representation


	#TODO - support for __match_args__

	#TODO - deprecate field_configuration and use functions? Or?
	positional = field_configuration(required=True)
	optional = field_configuration(default=None)
	all_positional = field_configuration(remaining_positionals=True)
	all_named = field_configuration(remaining_named=True)

	NOT_SET = object()

	def setting(value=NOT_SET, **settings):
		if value is NOT_SET:
			return field(positional=False, field_type=SETTING, **settings)
		else:
			return field(default=value, field_type=SETTING, positional=False, **settings)


	def state(value=NOT_SET, **settings):
		#TODO - implement this in other places (could improve too)
		use_settings = dict(
			positional=False,
			named=False,
		)
		use_settings.update(settings)

		if value is NOT_SET:
			return field(**use_settings)
		else:
			return field(default=value, **use_settings)

	def constant(value=NOT_SET, **settings):
		if value is NOT_SET:
			return field(read_only=True, positional=False, named=False, **settings)
		else:
			return field(default=value, read_only=True, positional=False, named=False, **settings)

	def named(value=NOT_SET, **settings):
		if value is NOT_SET:
			return field(positional=False, named=True, **settings)
		else:
			return field(default=value, positional=False, named=True, **settings)

	def factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=positionals, factory_named=named, positional=False, named=False)

	def bound_factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=(SELF, *positionals), factory_named=named, positional=False, named=False)

	def optional_factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=positionals, factory_named=named)

	def optional_bound_factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=(SELF, *positionals), factory_named=named)


	def read_only_factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=positionals, factory_named=named, positional=False, named=False, read_only=True)

	def read_only_bound_factory(factory, *positionals, **named):
		return field(factory=factory, factory_positionals=(SELF, *positionals), factory_named=named, positional=False, named=False, read_only=True)


	def constructor_constant(value=NOT_SET):
		if value is NOT_SET:
			return field(required=True, read_only=True)
		else:
			return field(default=value, read_only=True)



	factory_self_reference = dict(
		factory_positionals=(SELF,),
	)


