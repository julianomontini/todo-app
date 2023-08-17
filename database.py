from flask_sqlalchemy import SQLAlchemy
from app import app
from decouple import config

app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URI')
db = SQLAlchemy(app)