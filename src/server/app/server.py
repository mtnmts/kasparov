import os

from flask import Flask
from flask_restful import Resource, Api

basedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')

app = Flask(__name__, template_folder="../../client", static_folder="../../client", static_url_path="/static")
app.config.from_object('app.config')

# set the secret key.  keep this really secret:
app.secret_key = 'TheyellowchimpanSEEE3030LetsGooftheMonkeyinS5E01GOTisCrazyLoveThatShow?@!?!$FuckFuck!!'

# flask-restful
api = Api(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


import views

api.add_resource(views.Website, '/api/website')
app.add_url_rule('/', view_func=views.ShowIndex.as_view('show_index'))