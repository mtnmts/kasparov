import json
import itertools
cont = itertools.count()

class Target(object):
	def __init__(self, ip, password, user='root'):
		self.ip = ip
		self.user = user
		self.password = password
		self.id = cont.next()

	def __repr__(self):
		return "<Target IP:{ip}>".format(ip=self.ip)

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__)