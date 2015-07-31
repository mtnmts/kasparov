from flask.views import View
from flask import render_template, request, abort
from flask_restful import Api, Resource
from flask_restful import reqparse
from app.models import RemoteServer
import json
from app.server import api, app
from app.models import db
class ShowIndex(View):
    def dispatch_request(self):
        return render_template('index.html')

class Website(Resource):
	def post(self):
		json_data = request.get_json(force=True)
		rs = RemoteServer(json_data['ip'], json_data['pass'])
		db.session.add(rs)
		db.session.commit()
		return {'server_id' : rs.id}

	def get(self):
		resp = RemoteServer.Schema(many=True).dump(RemoteServer.query.all())
		print resp.data
		return resp.data

class WebsiteSpecific(Resource):
	def get(self, site_id):
		item = RemoteServer.Schema().dump(RemoteServer.query.get(site_id)).data
		print item
		if not item:
			return abort(500)
		return item

api.add_resource(Website, '/api/website')
api.add_resource(WebsiteSpecific, '/api/website/<int:site_id>')
app.add_url_rule('/', view_func=ShowIndex.as_view('show_index'))
