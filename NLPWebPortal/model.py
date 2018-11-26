from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from NLPWebPortal import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('user_id', Integer, primary_key=True)
    email = db.Column('email', String(50), unique=True, index=True)
    password = db.Column('password', String)

    def __init__(self, email, password):
        self.email = email
        self.password = password        

    def is_active(self):
        return True

    def get_id(self):
        return (self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
