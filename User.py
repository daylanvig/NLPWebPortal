from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class User(db):
    __tablename__ = 'users'
    id = Column('user_id', Integer, primary_key=True)
    email = Column('email', String(50), unique=True, index=True)
    password = Column('password', String)
    models = relationship('LanguageModel', backref='user', lazy='dynamic')

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

class LanguageModel(db):
    __tablename__ = "LanguageModel"

    id = Column('model_id', Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))

