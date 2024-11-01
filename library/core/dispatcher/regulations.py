from .. import record as R

#TODO - move to proper place
def API_Requirement(*pos):
	pass




class Abstract_Regulations(R.Record):
	extend = API_Requirement('Method(self, source: list)')
	derive = API_Requirement('Method(self)')
	aggregate_matches = API_Requirement('Meth(self, aggregator:Abstract_Aggregator, item)')


class Regulations(Abstract_Regulations):
	rules: R.Field(factory=list)

class LUT_Regulations(Abstract_Regulations):
	rules: R.Field(factory=dict)
