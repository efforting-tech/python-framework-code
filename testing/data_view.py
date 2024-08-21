from efforting.mvp6.data_view import View_Definition, Field_Conversion_Rule, Initializer


view_def = View_Definition(
	int = Field_Conversion_Rule('float', int) | Field_Conversion_Rule('string', int) | Initializer(0),
	float = Field_Conversion_Rule('string', float) | Field_Conversion_Rule('int', float) | Initializer(0.0),
	string = Field_Conversion_Rule('int', str) | Field_Conversion_Rule('float', str) | Initializer('0'),
)

instance = view_def()

print(repr(instance.float))
print(repr(instance.string))
