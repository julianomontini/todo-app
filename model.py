from database import db
from sqlalchemy.orm import declarative_base
from app import app
from datetime import datetime
from sqlalchemy import event

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class ToDo(Base):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    due_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='created')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))


with app.app_context():
    Base.metadata.create_all(db.engine)