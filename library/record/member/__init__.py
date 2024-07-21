from ..rudimentary import define_record, Abstract_Record

#TODO - move to ABC
class Abstract_Member(Abstract_Record):
	pass

define_record('positional', named=dict(
	default=None,
	factory=None,
), bases=(Abstract_Member,))

define_record('named', named=dict(
	default=None,
	factory=None,
), bases=(Abstract_Member,))


define_record('all_named', bases=(Abstract_Member,))
define_record('all_positional', bases=(Abstract_Member,))


#TODO - when constant is used by type system it should not allow writes, but now it is just like any positional or named entry. This entire file should be seen as a stub for the moment.
define_record('constant', named=dict(
	default=None,
	factory=None,
), bases=(Abstract_Member,))
