def unpack_dict(target, *keys):
	yield from (target[k] for k in keys)
