from ..rudimentary import define_record, Abstract_Record, Value
from ... import ABC, symbol

#TODO - we must make it so that M.positional() is different from M.positional(...) by having default be symbol.not_set
#		this was started to be implemented but got a bit messy and it should be addressed soon

define_record('positional', named=dict(
	default=None,
	factory=None,
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))

define_record('named', named=dict(
	default=None,
	factory=None,
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))

define_record('all_named', named=dict(
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))

define_record('all_positional', named=dict(
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))


#TODO - when constant is used by type system it should not allow writes, but now it is just like any positional or named entry. This entire file should be seen as a stub for the moment.
define_record('constant', named=dict(
	default=None,
	factory=None,
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))


define_record('state', named=dict(
	default=None,
	factory=None,
	repr=Value(True),
), bases=(Abstract_Record,), decorators=(ABC.Record.Member,))
