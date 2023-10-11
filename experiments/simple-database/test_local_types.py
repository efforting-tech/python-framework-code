import local_types as T

#TODO - increase coverage

def common_test_set_operations(test_type):
	class set_operations(Test, title='Test set operations'):
		class union(Test, title='Union set operation'):
			s1 = test_type(["a", "b", "c"])
			s2 = test_type(["c", "d", "e"])
			assert list(s1 | s2) == ["a", "b", "c", "d", "e"]

		class difference(Test, title='Difference set operation'):
			s1 = test_type(["a", "b", "c"])
			s2 = test_type(["b", "c", "d"])
			assert list(s1 - s2) == ["a"]

		class intersection(Test, title='Intersection set operation'):
			s1 = test_type(["a", "b", "c"])
			s2 = test_type(["b", "c", "d"])
			assert list(s1 & s2) == ["b", "c"]

class ordered_set(Test, skip=False):
	class insertion(Test, index=0, title='Test adding elements and ordering'):
		s = T.ordered_set()
		s.insert(0, 'a')
		s.insert(1, 'b')
		s.insert(2, 'c')
		assert list(s) == ['a', 'b', 'c']

	class insertion(Test, index=1, title='Test adding duplicate elements and preserving order'):
		s.insert(0, 'a')
		assert list(s) == ['a', 'b', 'c']

	class update(Test, title='Test updating elements and preserving order'):
		s[1] = 'd'
		assert list(s) == ['a', 'd', 'c']

	class removing(Test, title='Test removing elements and preserving order'):
		del s[0]
		assert list(s) == ['d', 'c']

	class iteration(Test, title='Test iterating over the set'):
		assert [element for element in s] == ['d', 'c']

	class discard(Test, title='Test discarding'):
		s.discard('d')
		assert list(s) == ['c']

	class add(Test, title='Test adding'):
		s.add('e')
		assert list(s) == ['c', 'e']

	common_test_set_operations(T.ordered_set)


class unordered_set(Test, title='Testing unordered_set', skip=False):
	class add(Test, title='Test adding elements'):
		s = T.unordered_set()
		s.add('a')
		s.add('b')
		assert 'a' in s
		assert 'b' in s

	class add_duplicate(Test, index=1, title='Test adding duplicate elements'):
		s = T.unordered_set()
		s.add('a')
		s.add('b')
		s.add('a')
		s.add('b')
		assert len(s) == 2

	class remove(Test, title='Test removing elements'):
		s = T.unordered_set()
		s.add('a')
		s.add('b')
		s.remove('a')
		assert 'a' not in s

	class contains(Test, title='Test checking elements'):
		s = T.unordered_set()
		s.add('b')
		assert 'b' in s
		assert 'c' not in s

	class iterate(Test, title='Test iterating over the set'):
		s = T.unordered_set()
		s.add('b')
		assert sorted([element for element in s]) == ['b']



class ordered_dict(Test):
	class add(Test, title='Test adding elements and ordering'):
		d = T.ordered_dict()
		d[0] = 'a'
		d[1] = 'b'
		d[2] = 'c'
		assert list(d.values()) == ['a', 'b', 'c']
		assert list(d.keys()) == [0, 1, 2]

	class update(Test, title='Test updating elements and preserving order'):
		d = T.ordered_dict()
		d[0] = 'a'
		d[1] = 'b'
		d[2] = 'c'
		d[1] = 'd'
		assert list(d.values()) == ['a', 'd', 'c']

	class remove(Test, title='Test removing elements and preserving order'):
		d = T.ordered_dict()
		d[0] = 'a'
		d[1] = 'b'
		d[2] = 'c'
		del d[0]
		assert list(d.values()) == ['b', 'c']
		assert list(d.keys()) == [1, 2]

	class iterate(Test, title='Test iterating over the dict'):
		d = T.ordered_dict()
		d[0] = 'a'
		d[1] = 'b'
		d[2] = 'c'
		assert [(k,v) for k,v in d.items()] == [(0, 'a'), (1, 'b'), (2, 'c')]

	class insert(Test, title='Test insertion'):
		# Create an ordered_dict and add some initial values
		d = T.ordered_dict(hamster='fluffy', ball='round', door='rectangular')

		# Insert a new key-value pair using the insert method
		d.insert(2, 'car', 'red')

		# Assert that the contents are correct
		assert list(d.keys()) == ['hamster', 'ball', 'car', 'door']
		assert list(d.values()) == ['fluffy', 'round', 'red', 'rectangular']


class unordered_dict(Test):
	class add(Test, title='Test adding elements'):
		d = T.unordered_dict()
		d[0] = 'a'
		d[1] = 'b'
		d[2] = 'c'
		assert set(d.values()) == {'a', 'b', 'c'}
		assert set(d.keys()) == {0, 1, 2}


class adding_elements(Test, title='Test adding elements in order'):
	l = T.list()
	l.insert(0, 'a')
	l.insert(1, 'b')
	l.insert(2, 'c')
	assert list(l) == ['a', 'b', 'c']

class updating_elements(Test, title='Test updating elements'):
	l = T.list()
	l.insert(0, 'a')
	l.insert(1, 'b')
	l.insert(2, 'c')
	l[1] = 'd'
	assert list(l) == ['a', 'd', 'c']

class removing_elements(Test, title='Test removing elements'):
	l = T.list()
	l.insert(0, 'a')
	l.insert(1, 'b')
	l.insert(2, 'c')
	del l[0]
	assert list(l) == ['b', 'c']

class iterating_elements(Test, title='Test iterating over the list'):
	l = T.list()
	l.insert(0, 'a')
	l.insert(1, 'b')
	l.insert(2, 'c')
	assert [element for element in l] == ['a', 'b', 'c']


class bag(Test, title='Testing bag', skip=False):
	class adding_elements(Test, title='Test adding elements'):
		b = T.bag()
		b.add('a')
		b.add('b')
		assert sorted(b) == ['a', 'b']

	class adding_duplicate_elements(Test, title='Test adding duplicate elements'):
		b = T.bag()
		b.add('a')
		b.add('b')
		b.add('b')
		assert sorted(b) == ['a', 'b', 'b']

	class removing_elements(Test, title='Test removing elements'):
		b = T.bag()
		b.add('a')
		b.add('b')
		b.remove_all('a')
		assert 'a' not in b

	class checking_elements(Test, title='Test checking elements in the bag'):
		b = T.bag()
		b.add('b')
		assert 'b' in b
		assert 'c' not in b

	class iterating_elements(Test, title='Test iterating over the bag'):
		b = T.bag()
		b.add('b')
		b.add('b')
		b.add('b')
		assert sorted(b) == ['b', 'b', 'b']
