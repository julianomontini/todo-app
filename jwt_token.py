from flask_jwt_extended import JWTManager
from app import app
from datetime import timedelta
from decouple import config

app.config['JWT_SECRET_KEY'] = config('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_ISSUER'] = config('JWT_ISSUER')
app.config['JWT_IDENTITY_CLAIM'] = 'id'

jwt = JWTManager(app)