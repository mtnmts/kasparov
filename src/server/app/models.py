import json
import itertools
from marshmallow import Schema, fields
from flask.ext.sqlalchemy import SQLAlchemy

cont = itertools.count()
db = SQLAlchemy()


class RemoteServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(120))

    def __init__(self, host, password):
        self.username = 'root'
        self.host = host
        self.password = password

    def __repr__(self):
        return "<Server %s>" % self.host

    class Schema(Schema):
        host = fields.String()
        username = fields.String()
        password = fields.String()

class Target(object):

    def __init__(self, ip, password, user='root', uid=-1):
        self.ip = ip
        self.user = user
        self.password = password
        self.id = uid

    def set_id(self, uid):
        self.id = uid

    def __repr__(self):
        return "<Target IP:{ip}>".format(ip=self.ip)

    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

