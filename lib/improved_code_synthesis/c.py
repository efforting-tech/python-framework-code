from .. import type_system as RTS
from ..type_system.bases import public_base
from ..text_nodes import text_node

class structure(public_base):
	name = RTS.positional()
	members = RTS.factory(dict)

class structure_member(public_base):
	name = RTS.positional()
	definition = RTS.positional(default=None)
	comment = RTS.positional(default=None)


def render_structure(struct):



	body = list()
	for member in struct.members.values():
		if member.comment:
			body.append(f'{member.definition}\t{member.name};	// {member.comment}')
		else:
			body.append(f'{member.definition}\t{member.name};')

	return text_node((
		f'struct {struct.name} {{',
			*text_node(body).indented_copy().lines,
		'};'
	))
