from efforting.mvp6.core import record as R


class thing(R.Record):
	stuff: R.Field()

print(thing.stuff)
exit()

class majig(R.Record):
	world: thing.stuff


exit()

class AGR:
	class First_Result:
		pass

	class Result_List:
		pass

class Regex_Regulations:
	pass

class Dispatcher_Factory(type):
	@classmethod
	def __prepare__(factory, name, bases):
		fields = dict()


		for base in bases:
			fields.update(base.__annotations__)

		return dict(__annotations__=fields)

	@classmethod
	def __new__(factory, cls, name, bases, scope):
		print('INIT', name, bases)
		return super().__new__(factory, name, bases, scope)


class Core_Dispatcher(R.Record):

	def __init_subclass__(cls):
		anno = cls.__annotations__
		configuration = dict(anno)
		anno.clear()

		for base in cls.mro():
			if base is object:
				continue

			for key, value in base.__annotations__.items():
				if key not in anno:
					anno[key] = value

		print(anno)

		if item_aggregator_factory := configuration.get('item_aggregator'):
			anno['item_aggregator'] = R.Field(factory=item_aggregator_factory)



		super().__init_subclass__()




class Dispatcher(Core_Dispatcher):
	item_aggregator: AGR.First_Result
	collection_aggregator: AGR.Result_List

class Processor(Dispatcher):
	pass

class Transformer(Dispatcher):
	pass

class Core_Regex_Dispatcher(Core_Dispatcher):
	regulations: Regex_Regulations

class Regex_Processor(Core_Regex_Dispatcher, Processor):
	pass

class Regex_Transformer(Core_Regex_Dispatcher, Transformer):
	pass



#print(Processor().regulations)
#print(Core_Regex_Dispatcher.__annotations__)