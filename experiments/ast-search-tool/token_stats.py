import __main__
from pathlib import Path
from collections import Counter

stats = Counter()
prune_length = 1000
prune_threshold = 5000
pruning = True
prune_counter = 0

def measure_frequency(x):
	return x[1]

def measure_length(x):
	return len(x[0][1])

def measure_product_of_length_and_frequency(x):
	#We will skip counts of one
	if x[1] == 1:
		return 0
	return len(x[0][1]) * x[1]

measure = measure_product_of_length_and_frequency

for index, source in enumerate(__main__.cr.sources.values()):
	#print(dir(source))
	for left, right, token in source.token_markings:
		key = (token.type, token.string)

		stats[key] += 1

	if pruning and len(stats) > prune_threshold:
		pruned = sorted(stats.items(), key=measure, reverse=True)[:prune_length]
		stats.clear()
		for key, count in pruned:
			stats[key] = count

		prune_counter += 1


print(f'There are {len(__main__.cr.sources)} files.')
print(f'Pruning occured {prune_counter} times.')
print()

def nrepr(v):
	token, value = v
	r = repr(value)
	if len(r) > 100:
		r = r[:100] + f'\N{horizontal ellipsis} ({len(value)})'

	return f'({token}, {r})'

for key, count in sorted(stats.items(), key=measure, reverse=True)[:250]:
	print(f'{count} × {nrepr(key)}')
