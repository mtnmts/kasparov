from flask.views import View
from flask import render_template, request, abort
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
		t_id = globs.TARGETS.add(Target(json_data['ip'],json_data['pass']))
		print json_data
		return {'server_id' : t_id}

	def get(self):
		return [json.loads(g.to_JSON()) for g in globs.TARGETS.all()]

class WebsiteSpecific(Resource):
	def get(self, site_id):
		if not globs.TARGETS.exists(site_id):
			return abort(500)
		t =  json.loads(globs.TARGETS.get(int(site_id)).to_JSON())
		return t

# class Install(Resource):
# 	def post(self):
# 		json_data = request.get_json(force=true)
# 		install_target = globs.get((json_data['id']))
		