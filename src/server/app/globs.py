import itertools


class Targets(object):
	def __init__(self):
		self._targets = {}
		self._counter = itertools.count()
	

	def add(self,t):
		i = self._counter.next()
		t.set_id(i)
		self._targets[i] = t

	def get(self,i):
		return self._targets[i]

	def all(self):
		return self._targets.values()

	def exists(self, i):
		return True if i in self._targets else False


TARGETS = Targets()
