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
		globs.TARGETS.append(Target(json_data['ip'],json_data['pass']))
		return {'server_id' : len(globs.TARGETS) - 1}

	def get(self):
		return [json.loads(g.to_JSON()) for g in globs.TARGETS]

class WebsiteSpecific(Resource):
	def get(self, site_id):
		if int(site_id) > len(globs.TARGETS):
			print "SiteID: " + str(site_id), " GlobalLen:" + str(len(globs.TARGETS))
			print "SiteID TYPE: " + type(site_id)
			return abort(500)
		t =  json.loads(globs.TARGETS[int(site_id)].to_JSON())
		return t

class Install(Resource):
	def post(self):
		json_data = request.get_json(force=true)
		install_target = globs[int(json_data['id'])]
		