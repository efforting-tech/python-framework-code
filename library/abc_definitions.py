from . import abc_factory as AF

root_symbol = AF.create_ABC_Symbol('ABC')
AF.register_abc_at_target(root_symbol, '''

	Factory
	Record.Data_Descriptor
	Record
	Sequence
	Mapping
	Record.Member
	Text.Block
	Text.Line

	Action
	Decorator
	Data_Condition

	Processor_State

''')
