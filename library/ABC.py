from . import abc_factory as _AF

_root =_AF.create_ABC_Node(__name__.rsplit('.')[-1])
_root._set_auto_graft_here()
_AF.register_abc_at_target(_root, '''

	Factory
	Record.Data_Descriptor
	Record
	Record.Member
	Text.Block
	Text.Line

''')


