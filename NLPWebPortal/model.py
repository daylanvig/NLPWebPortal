from flask_sqlalchemy import SQLAlchemy
from NLPWebPortal import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


#User account information
class User(db.Model):

    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, index=True)
    pw_hash = db.Column(db.String)
    registered_on = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    training = db.relationship('TrainingFile', backref='user', lazy=True)

    def __init__(self, email, password):
        self.email = email
        self.set_password(password)      
        self.registered_on = datetime.utcnow()

    def is_active(self):
        return True

    def get_id(self):
        return (self.user_id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    #Generates a hashed password
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def __repr__(self):
        return '<User Email %r>' % (self.email)

#Store training file meta information
class TrainingFile(db.Model):

    file_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    file_name = db.Column(db.String(50), nullable=False)
    extension = db.Column(db.String(5), nullable=False)
    cleaned = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, upload_name, extension):
        self.user_id = user_id
        self.file_name = upload_name
        self.extension = extension
        self.upload_date = datetime.utcnow()

    def get_id(self):
        return (self.file_id)

