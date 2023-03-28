import time, sys, subprocess, io
from collections import deque
from traceback import print_exception

log_stubs = False
stub_log = list()

def stub(message):
	if log_stubs:
		stub_log.append((time.monotonic(), code_path_to_here(1), message))


def get_frame_name(frame):
	if frame.f_code.co_name == '<module>':
		module_name = frame.f_globals['__name__']
		return f'm {module_name}'
	else:
		return f'\N{MATHEMATICAL ITALIC SMALL F} {frame.f_code.co_name}'

def code_path_to_here(stack_offset=0, stop_at_module=True):
	frame = sys._getframe(stack_offset + 1)
	stack = deque()
	while frame:
		stack.appendleft(frame)

		if stop_at_module and frame.f_code.co_name == '<module>':
			break

		frame = frame.f_back

	return ' → '.join(get_frame_name(f) for f in stack)


#TODO: have a data module with various units and use that
time_units = dict()
time_units['ns'] = 1e-9
time_units['µs'] = 1e-6
time_units['ms'] = 1e-3
time_units['s'] = 1e0
time_units['m'] = 60 * time_units['s']
time_units['h'] = 60 * time_units['m']
time_units['d'] = 24 * time_units['h']
time_units['w'] = 7 * time_units['d']
time_units['y'] = (365 + 1/4 - 1/100 + 1/400) * time_units['d']

time_units_in_order = sorted(time_units.items(), key=lambda i: i[1], reverse=True)

def human_delta_time(dt, default_unit='s'):
	for unit, weight in time_units_in_order:
		if (value := dt / weight) > 0.1:
			return f'{value:.2f} {unit}'

	value = dt / time_units[default_unit]
	return f'{value:.2f} {default_unit}'


def print_stub_log():
	first_time = None
	for mt, cp, msg in stub_log:
		if first_time is None:
			first_time = mt

		dt = mt - first_time
		print(f'{human_delta_time(dt):<12}:{cp} # {msg}')


#TODO - features that can check GC that local types are registered and that API checks are enforced (if we want that)


#TODO - should be moved to proper place
def cexp(condition, *pieces):
	return pieces if condition else ()

def cde(condition, **pieces):
	return pieces if condition else {}


def cexp_unzip(*zipped):
	iterator = iter(zipped)
	for condition in iterator:
		pieces = next(iterator)
		if condition:
			yield from pieces


def stdout_grep(pattern, case_insensitive=False, invert=False, extended=False):
	proc = subprocess.Popen(('grep', '-n',
		*cexp_unzip(
			case_insensitive, 	('-i',),
			invert, 			('-v',),
			extended, 			('-E',),
		),
		pattern, '--color=always'), stdin=subprocess.PIPE, stdout=sys.stdout
	)
	sys.stdout = io.TextIOWrapper(proc.stdin)

def stdout_head(lines=50):
	proc = subprocess.Popen(('head', '-n', str(lines)), stdin=subprocess.PIPE, stdout=sys.stdout)
	sys.stdout = io.TextIOWrapper(proc.stdin)

def stderr_grep(pattern, case_insensitive=False, invert=False, extended=False):
	proc = subprocess.Popen(('grep', '-n',
		*cexp_unzip(
			case_insensitive, 	('-i',),
			invert, 			('-v',),
			extended, 			('-E',),
		),
		pattern, '--color=always'), stdin=subprocess.PIPE, stderr=sys.stderr
	)
	sys.stderr = io.TextIOWrapper(proc.stdin)

def stderr_head(lines=50):
	proc = subprocess.Popen(('head', '-n', str(lines)), stdin=subprocess.PIPE, stderr=sys.stderr)
	sys.stderr = io.TextIOWrapper(proc.stdin)


def use_linecache_traceback():
	sys.excepthook = print_exception
