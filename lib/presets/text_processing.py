from .. import rudimentary_type_system as RTS
from ..data_utils import stack, attribute_stack

from ..development_utils import stdout_head, stdout_grep, stderr_head, stderr_grep
from ..development_utils.introspection import introspect

#from ..rudimentary_features.code_manipulation.templating.template_renderer import simple_template_renderer
#from ..rudimentary_features.code_manipulation.templating.text_templates import template_context, custom_template_tokenizer, pending_text_template
from ..rudimentary_features.code_manipulation.templating import template_classifications as TC


from ..rudimentary_type_system.bases import public_base
from ..rudimentary_type_system.representation import adjust_field_stack_limit
from ..table_processing.table import table


from ..text_nodes import text_node
#from ..text_processing.tokenization import token_match, tokenizer, yield_match, yield_matched_text, yield_classification, SKIP, yield_value, yield_match_and_value, call_processor_for_match
from ..text_processing.tokenization import SKIP, yield_value, call_processor_for_match

from ..text_processing.re_tokenization import literal_re_pattern
from ..text_processing.priority_processing import simple_priority_parser_for_regular_expressions, simple_priority_replacer
from ..symbols import register_symbol, create_symbol, register_multiple_symbols
from ..rudimentary_types.generic_tabular_mapping import one_to_one_mapping	#Previously strict_binary_mapping

from ..symbols.directory import symbol_node

from pathlib import Path
import time, re, itertools
from collections import defaultdict, deque
