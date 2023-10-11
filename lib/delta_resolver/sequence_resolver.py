#Here we will create a class that can deal with edit distance, clean things up a bit so we can do better experiments.

from .. import type_system as RTS
from ..type_system.bases import public_base
from ..symbols import register_symbol
from .operations import sequence as OP

#What about if we always do head-body-tail substitutions? NO
#Let's do graph based search, preferably defined in a way so it can work on AST as well.

def branch(resolver, s1, s2, branch):
	i1 = 0
	i2 = 0
	m_len = 0
	d_len = 0
	while i1 < len(s1) and i2 < len(s2):
		if s1[i1] == s2[i2]:
			if d_len:
				print('diff', d_len)

			d_len = 0

			m_len += 1
			i1 += 1
			i2 += 1

		else:
			d_len += 1

			if m_len:
				print('match', m_len)
			m_len = 0

			if branch == 0:
				i1 += 1
			elif branch == 1:
				i2 += 1
			else:
				raise Exception()


	if d_len:
		print('T-diff', d_len)

	if m_len:
		print('T-match', m_len)


class oldbranch(public_base):
	resolver = RTS.positional()
	s1 = RTS.positional()
	s2 = RTS.positional()
	branch = RTS.positional()
	i1 = RTS.state(0)
	i2 = RTS.state(0)

	m_len = RTS.state(0)

	d_start = RTS.state()
	d_len = RTS.state(0)


	def reset_match(self):
		self.m_len = 0

	def reset_diff(self):
		self.d_start = (self.i1, self.i2)[self.branch]
		self.d_len = 0


	def check_match(self):
		if self.m_len:
			v = (self.s1, self.s2)[self.branch]
			e = (self.i1, self.i2)[self.branch]
			s = e - self.m_len
			print(f'match {v[s:e]!r}')

	def check_diff(self):
		if self.d_len:
			print('DIFF', self.d_len)

			#print(f'diff {r1!r} → {r2!r}')

	def __iter__(self):

		self.reset_match()
		self.reset_diff()

		while self.i1 < len(self.s1) and self.i2 < len(self.s2):
			if self.s1[self.i1] == self.s2[self.i2]:
				self.check_diff()
				self.reset_diff()
				self.m_len += 1
				self.increment_both()

			else:
				self.d_len += 1

				self.check_match()
				self.reset_match()

				self.increment_branch()

		print('tail')
		deleted = len(self.s1) - self.i1
		inserted = len(self.s2) - self.i2
		print('insdel', inserted, deleted)

		if inserted:
			print(f'inserted {self.s2[-inserted:]!r}')

		elif deleted:
			print(f'deleted {self.s1[-deleted:]!r}')

		yield from ()

	def increment_both(self):
		self.i1 += 1
		self.i2 += 1

	def increment_branch(self):
		if self.branch == 0:
			self.i1 += 1
		elif self.branch == 1:
			self.i2 += 1
		else:
			raise Exception()



class sequence_delta_resolver(public_base):
	minimum_branch_measure = RTS.setting(1.0)

	cost_of_insert_op = RTS.setting(1.0)
	cost_of_delete_op = RTS.setting(1.0)
	cost_of_replace_op = RTS.setting(1.0)

	cost_of_insert_item = RTS.setting(1.0)
	cost_of_delete_item = RTS.setting(1.0)
	cost_of_replace_item = RTS.setting(1.0)

	reversible = RTS.setting(False)

	def resolve(self, s1, s2):

		if s1 == s2:
			return

		print('b1')
		print(branch(self, s1, s2, 0))
		print('b2')
		print(branch(self, s1, s2, 1))

		yield from ()


if False:	#Archived



	#TODO: Is replace directly followed by insert? Or is it replace + match + insert? If match length is small we could post process it together - but this is future improvements
	#		maybe operations should contain a bit more data and we can throw some of it away?

	class sequence_low_level_operation:
		operand = register_symbol('internal.delta.sequence.operand')
		insert = operand()
		delete = operand()
		replace = operand()
		match = operand()

	class sequence_operation:
		class insert(public_base):
			start = RTS.field()
			length = RTS.field(default=1)

		class delete(public_base):
			start = RTS.field()
			length = RTS.field(default=1)

		class replace(public_base):
			start = RTS.field()
			delta = RTS.field(default=0)
			length = RTS.field(default=1)
			delta_length = RTS.field(default=0)

		class matches(public_base):
			start = RTS.field()
			delta = RTS.field(default=0)
			length = RTS.field(default=1)
			delta_length = RTS.field(default=0)



	class sequence_delta_resolver(public_base):
		minimum_branch_measure = RTS.setting(1.0)
		reversible = RTS.setting(False)

		#def resolve_delta(self, s1, s2):
			#return self.post_process(self.to_streaks(self.expand(self.cmp_branch(s1, s2), s1, s2)))

		def resolve(self, s1, s2):
			if self.reversible:
				return self.resolve_reversible(s1, s2)
			else:
				return self.resolve_non_reversible(s1, s2)

		def resolve_non_reversible(self, s1, s2):
			pd = 0
			for op in self.post_process(self.to_streaks(self.expand(self.cmp_branch(s1, s2), s1, s2))):
				#print(op)
				match op:
					case sequence_operation.replace():
						yield OP.non_reversible.replace(op.start + pd,
							op.length,
							s2[op.start + op.delta : op.start + op.delta + op.length + op.delta_length],
						)

					case sequence_operation.delete():
						yield OP.non_reversible.delete(op.start + pd,
							op.length,
						)

					case sequence_operation.insert():
						yield OP.non_reversible.insert(op.start + pd,
							s2[op.start: op.start + op.length],
						)

					case _ as unhandled:
						raise Exception(f'The value {unhandled!r} could not be handled')


		def resolve_reversible(self, s1, s2):
			pd = 0
			for op in self.post_process(self.to_streaks(self.expand(self.cmp_branch(s1, s2), s1, s2))):
				match op:
					case sequence_operation.replace():
						yield OP.reversible.replace(op.start + pd,
							s1[op.start : op.start + op.length],
							s2[op.start + op.delta : op.start + op.delta + op.length + op.delta_length],
						)
						pd += op.delta_length

					case sequence_operation.delete():
						yield OP.reversible.delete(op.start + pd,
							s1[op.start: op.start + op.length],
						)

					case sequence_operation.insert():
						yield OP.reversible.insert(op.start + pd,
							s2[op.start: op.start + op.length],
						)

					case _ as unhandled:
						raise Exception(f'The value {unhandled!r} could not be handled')


		#TODO rename these methods to better names
		def cmp_branch(self, s1, s2, i1=0, i2=0, di1=1, di2=1, no_branch=False):
			while i1 < len(s1) and i2 < len(s2):
				if s1[i1] == s2[i2]:
					yield True, i1, i2
					i1 += 1
					i2 += 1

				else:
					if no_branch:
						i1 += di1
						i2 += di2
					else:
						branch1 = tuple(self.cmp_branch(s1, s2, i1, i2, 1, 0, True))
						branch2 = tuple(self.cmp_branch(s1, s2, i1, i2, 0, 1, True))


						#The problem to turn to streaks here is that cmp does the more fancy reporting compared to cmp_branch. We will try again in t7
						bs1 = tuple(self.post_process(self.to_streaks(self.expand(branch1, s1, s2))))
						bs2 = tuple(self.post_process(self.to_streaks(self.expand(branch2, s1, s2))))

						bs1_m = self.measure(bs1)
						bs2_m = self.measure(bs2)

						#print(bs1, bs2, bs1_m, bs2_m)

						if bs1 and bs1_m > bs2_m and bs1_m > self.minimum_branch_measure:
							yield from branch1
							op, i1, i2 = branch1[-1]

						elif bs2 and bs2_m > bs1_m and bs2_m > self.minimum_branch_measure:
							yield from branch2
							op, i1, i2 = branch2[-1]
						else:
							yield False, i1, i2

						i1 += 1
						i2 += 1



		def measure(self, streak_sequence):
			length = 0
			for s in streak_sequence:
				length += s.length
			return length / (1 + len(streak_sequence))**2


		def expand(self, gen, s1, s2):
			last = None
			for matched, i1, i2 in gen:
				if last:
					li1, li2 = last
					di1, di2 = i1 - li1, i2 - li2

					for i in range(li1+1, i1):
						yield sequence_low_level_operation.delete, i

					for i in range(li2+1, i2):
						yield sequence_low_level_operation.insert, i

				if matched:
					yield sequence_low_level_operation.match, i1, i2
				else:
					yield sequence_low_level_operation.replace, i1, i2

				last = (i1, i2)

			if last:
				for i in range(i1+1, len(s1)):
					yield sequence_low_level_operation.delete, i

				for i in range(i2+1, len(s2)):
					yield sequence_low_level_operation.insert, i



		def to_streaks(self, gen):
			last_op = None
			pending = None

			for o, *args in gen:
				if o is last_op:
					pending.length += 1

				else:
					if pending:
						yield pending

					match (o, *args):
						case [sequence_low_level_operation.delete, i]:
							pending =sequence_operation.delete(i)

						case [sequence_low_level_operation.insert, i]:
							pending = sequence_operation.insert(i)

						case [sequence_low_level_operation.match, i1, i2]:
							pending = sequence_operation.matches(i1, delta=i2-i1)

						case [sequence_low_level_operation.replace, i1, i2]:
							pending = sequence_operation.replace(i1, delta=i2-i1)

						case _ as unhandled:
							raise Exception(f'The value {unhandled!r} could not be handled')

				last_op = o

			if pending:
				yield pending


		def post_process(self, gen):
			pending = None
			last = None

			for index, item in enumerate(gen):
				if index == 0:
					match item:
						case sequence_operation.replace() | sequence_operation.matches():		#Can this happen to sequence_operation.replace?
							if item.start > 0:
								yield sequence_operation.delete(0, item.start)
							elif item.delta > 0:
								yield sequence_operation.insert(0, item.delta)


				match (last, item):
					case [sequence_operation.replace(), sequence_operation.insert(length=insert_length)]:
						pending.delta_length += insert_length

					case [sequence_operation.replace(), sequence_operation.delete(length=delete_length)]:
						pending.length += delete_length
						pending.delta_length -= delete_length

					case _:
						if pending:
							if not isinstance(pending, sequence_operation.matches):
								yield pending
						pending = item

				last = pending

			if pending:
				if not isinstance(pending, sequence_operation.matches):
					yield pending
