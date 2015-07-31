from app.server import db
from app.server import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)
db.create_all()
