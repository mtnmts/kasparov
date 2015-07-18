from flask.views import View
from flask import render_template, request
from flask_restful import Api, Resource
from flask_restful import reqparse
import globs
from models import Target
import json
class ShowIndex(View):
    def dispatch_request(self):
        return render_template('index.html')


class Website(Resource):
	def post(self):
		json_data = request.get_json(force=True)
		print json_data
		globs.TARGETS.append(Target(json_data['ip'],json_data['pass']))
		print globs.TARGETS

	def get(self):
		return [json.loads(g.to_JSON()) for g in globs.TARGETS]