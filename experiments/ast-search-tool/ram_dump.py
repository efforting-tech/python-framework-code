import __main__
from pathlib import Path

target = Path('/home/devilholk/ram_dump')

#print(target, __main__.cr)


#Create structure
for key in dict.fromkeys(s.parent for s in __main__.cr.sources):
	(target / key).mkdir(parents=True, exist_ok=True)

for source in __main__.cr.sources.values():
	target_path = target / source.path
	target_path.write_text(source.source)