#Experiment in GUI declaration

#from .. import rudimentary_type_system as RTS
#from ..rudimentary_type_system.bases import public_base

#from efforting.mvp4 import abstract_base_classes as abc
#from efforting.mvp4.self_test import abc



#print(isinstance('hello', registry.collection.identifiers))

from data_example import ar1
import ims_types as T
from ims_types import U



c = ar1.contents[0].contents

#c.append((10, 20))
#print(c)

from efforting.mvp4.function_utils.pattern_matching import check_match, create_extracting_function



test = (T.item_definition('Thing'), T.measure(20, U.joule))
check_match('(T.item_definition(), T.measure())', test)

c = create_extracting_function('(T.item_definition(name=item_name), T.measure(value=value, unit=unit))')
print(c(test)) # {'item_name': 'Thing', 'value': 20, 'unit': unit(unit(N/A, N/A, 'energy'), 'J', 'joule')}


#IDEA - we use typing with the structures, then we also add a feature to match tuples to structures when possible (this of course need to avoid overlap).
#		the important bit right now though is that typing works so that we can create rules for interacting with the data





#c = create_matching_function('(T.item_definition(), T.measure())')


#print(c((T.item_definition('Thing'), T.measure(20, U.joule))))






#print(abc.abc_metadata())

# Note - later when we want images: /srv/storage/Artifacts/Data/Personal Image Library

'''

	Step 1: What do we need?

		Manage grid layouts
			Searching, selecting, creating, modifying, deleting

		Manage containers
			Searching, selecting, creating, modifying, deleting, manage contents


	How could we define these things?

		FEAT Manage grid layouts

			FEAT View existing grids
				PRESENT list of predefined_grids
				WITH SUBSELECTION
					ACTION view grid
					ACTION edit grid
					ACTION delete grid

			FEAT Create new grid
				WITH NEW grid
					ACTION edit grid







'''


