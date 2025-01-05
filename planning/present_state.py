from efforting.tech.template1.core.debug.socket_based_logwriter import Indented_Socket_Log_Writer

writer = Indented_Socket_Log_Writer('localhost', 5003)

writer.print('Todo:')
with writer.indent(' '):
	writer.print(' ✅Check column table format')
	writer.print(' ✅Setup state table')
	writer.print(' ✅Create comparison feature')
	writer.print(' ✅Create unordered compare feature')
	writer.print(' ✨Work on first edge case')
	writer.print(' ✯ Setup multiple test cases')
	writer.print(' ✯ Tidy up')
writer.print()
writer.print(f"Happy New Year ✴{sum(n**3 for n in range(10))}✴")

