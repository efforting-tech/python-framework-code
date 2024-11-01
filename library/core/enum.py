if False:
	from .symbol import Symbol_Node, Symbol_Node_Reference



	#TO-DOC: Enum_Node_Reference can be copied using __getitem__ of Enum_Node which is different behavior from Symbol_Node_Reference. We should explain this in more detail and the reasoning behind it.
	class Enum_Node_Reference(Symbol_Node_Reference):
		def __getitem__(self, key):
			return self._target[key]

		def __eq__(self, other):
			if isinstance(other, Symbol_Node_Reference):	#TODO - ABC
				return self._target == other._target
			else:
				raise TypeError(self, other)	#TODO - Not implemented yet - should support Enum_Node

		def __hash__(self):
			return hash(self._target.path)

	class Enum_Node(Symbol_Node):

		def get_reference(self, create_new=False):
			return Enum_Node_Reference(self, create_new)

		def __eq__(self, other):
			if isinstance(other, Symbol_Node):	#TODO - ABC
				return self is other	#Underlying nodes are singletons
			else:
				raise TypeError(self, other)	#TODO - Not implemented yet - should support Enum_Node_Reference

		def __hash__(self):
			return hash(self.path)



		def __getitem__(self, key):
			if isinstance(key, Symbol_Node):	#TODOC - this is because we may want to filter strings/enum entries
				return key

			elif isinstance(key, int):
				return self.children[tuple(self.children)[key]].get_reference()	#Get by index


			else:
				ptr = self
				for piece in key.split('.'):
					ptr = getattr(ptr, piece)

				assert tuple(ptr._iter_children()) == ()	#TODO -proper exception
				return ptr




	def convert_symbol_to_enum(symbol):
		if isinstance(symbol, Symbol_Node):
			symbol.__class__ = Enum_Node
		else:
			raise TypeError(symbol)

