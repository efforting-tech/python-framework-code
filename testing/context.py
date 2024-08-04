from efforting.mvp6.context import context, context_dict_interface, execution_tracker, python_code_execution_interface

# code = '''

# def function():
# 	print(G)

# '''

# scope = dict()
# exec(code, scope)
# f = scope['function']

# print(f.__globals__ is scope)	#True

# scope['G'] = 123
# print(f())



r = context('test', dict(stuff=123))
sc = r.sub_context(dict(stuff=456, thing=123))

cdi = context_dict_interface(sc)
#cdi['stuff'] = 'hello'

et = execution_tracker()

r.set('et', et)


code = '''

#print(et.pending)
42/0
#stuff

'''

python_code_execution_interface.exec_in_context(sc, code, tracker=et)
#exec('stuff = 5\nprint(stuff)', dict(cdi), cdi.context.locals)


print(sc.locals['stuff'])

