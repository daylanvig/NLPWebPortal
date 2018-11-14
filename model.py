from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from routes import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('user_id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(50), unique=True, index=True)
    password = db.Column('password', db.String)
    models = db.relationship('LanguageModel', backref='user', lazy='dynamic')

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

class LanguageModel(db.Model):
    __tablename__ = "LanguageModel"

    id = db.Column('model_id', db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

