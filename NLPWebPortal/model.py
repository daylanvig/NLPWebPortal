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

  file_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
  file_name = db.Column(db.String(50), nullable=False)
  extension = db.Column(db.String(5), nullable=False)
  processed = db.Column(db.Boolean, default=False)
  upload_date = db.Column(db.DateTime, nullable=False)

  def __init__(self, user_id, upload_name, extension):
    self.user_id = user_id
    self.file_name = upload_name
    self.extension = extension
    self.upload_date = datetime.utcnow()

  def get_id(self):
    return (self.file_id)

  #for easy representation in processor
  def name(self):
    return (str(self.file_id) + '.' + self.extension)


class Dictionary(db.Model):

  word = db.Column(db.String, primary_key=True)
  count = db.Column(db.Integer, nullable=False)

  def __init__(self, word):
    self.word = word
    self.count = 1

  def increment(self):
    self.count = self.count + 1

  def __repr__(self):
    return "(%s, %d)" % (self.word, self.count)


class Query(db.Model):

  __tablename__ = 'query'

  query_id = db.Column(db.Integer, primary_key=True)
  query = db.Column(db.Text, nullable=False)
  result = db.Column(db.Text)
  type = db.Column(db.String(50))

  __mapper_args__ = {'polymorphic_identity': 'query', 'polymorphic_on': 'type'}

  def __init__(self, query):
    self.query = query


class UserQuery(Query):

  query_id = db.Column(
      db.Integer, db.ForeignKey('query.query_id'), primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
  use_private = (db.Boolean)
  request_date = db.Column(db.DateTime, nullable=False)

  __mapper_args__ = {'polymorphic_identity': 'userquery'}

  def __init__(self, query, user_id, use_private):
    Query.__init__(self, query)
    self.user_id = user_id
    self.use_private = use_private
    self.request_date = datetime.utcnow()


class TestQuery(Query):

  query_id = db.Column(
      db.Integer, db.ForeignKey('query.query_id'), primary_key=True)

  __mapper_args__ = {'polymorphic_identity': 'testquery'}

  def __init__(self, query, results_expected):
    Query.__init__(self, query)
