from flask_sqlalchemy import SQLAlchemy
from NLPWebPortal import db
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from termcolor import colored


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
  upload_date = db.Column(db.DateTime)

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

  def __init__(self, word, count):
    self.word = word
    self.count = count

  def increment(self, count):
    self.count = self.count + count

  def __repr__(self):
    return "(%s, %d)" % (self.word, self.count)


class Query(db.Model):

  __tablename__ = 'query'

  query_id = db.Column(db.Integer, primary_key=True)
  query_text = db.Column(db.Text, nullable=False)
  type = db.Column(db.String(50))

  __mapper_args__ = {'polymorphic_identity': 'query', 'polymorphic_on': 'type'}

  def __init__(self, query):
    self.query_text = query


class UserQuery(Query):

  query_id = db.Column(
      db.Integer, db.ForeignKey('query.query_id'), primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
  use_private = db.Column(db.Boolean, nullable=False)
  request_date = db.Column(db.DateTime, nullable=False)
  result = db.Column(db.Text)
  __mapper_args__ = {'polymorphic_identity': 'userquery'}

  def __init__(self, query, user_id, use_private, result):
    Query.__init__(self, query)
    self.user_id = user_id
    self.use_private = use_private
    self.request_date = datetime.utcnow()
    self.result = result


class TestQuery(Query):

  query_id = db.Column(
      db.Integer, db.ForeignKey('query.query_id'), primary_key=True)
  results_expected = db.Column(db.String)

  __mapper_args__ = {'polymorphic_identity': 'testquery'}

  def __init__(self, query, results_expected):
    Query.__init__(self, query)
    self.results_expected = ""

  def __repr__(self):
    return ' [%d]   %r' % (self.query_id, self.query_text)

  def detailed(self):
    return 'Fragment: %r \nExpected Result: %r' % (self.query_text,
                                                   self.results_expected)


class TestResult(db.Model):

  test_id = db.Column(db.Integer, primary_key=True)
  query_id = db.Column(
      db.Integer, db.ForeignKey('test_query.query_id'), nullable=False)
  report_id = db.Column(
      db.Integer, db.ForeignKey('report.report_id'), nullable=False)
  result = db.Column(db.String)
  is_correct = db.Column(db.Boolean)

  def __init__(self, query_id, report_id, result):
    self.query_id = query_id
    self.result = result
    self.report_id = report_id


class Report(db.Model):

  report_id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.Date, nullable=False)
  manual_evaluation = db.Column(db.Boolean, nullable=False)
  accuracy = db.Column(db.Numeric(scale=2))

  def __init__(self, manual):
    self.manual_evaluation = manual
    self.date = date.today()
    self.accuracy = 0

  def accuracy_calculate(self):
    """
    Calculates the accuracy of the report
    
    If the user selects manual evaluation, they are prompted for each test query. This is preferred
    as automatic evaluations risk false negatives - synonyms, variations in spelling, etc.
    If the user chooses automatic evaluation, they will be returned accuracy and given a chance to review
    any False tests to account for this.
    """

    tests = db.session.query(TestResult).filter(
        TestResult.report_id == self.report_id).all()
    failed_tests = []

    correct = 0
    if self.manual_evaluation == False:  #Automatic testing
      for t in tests:
        q = db.session.query(TestQuery).filter(
            TestQuery.query_id == t.query_id).first()
        if t.result.lower() == q.results_expected.lower():
          # If results match what was expected
          t.is_correct = True
          correct += 1
        else:
          t.is_correct = False
          failed_tests.append(t)
    else:  # Manual testing
      n_test = 1
      for t in tests:
        q = db.session.query(TestQuery).filter(
            TestQuery.query_id == t.query_id).first()
        print(('Query #%d: %r') % (n_test, q.query_text))
        print(('Results Expected: %r') % (q.results_expected))
        print(('Results: %r') % (t.result))
        isCorrect = input('Are results valid? [Y/N]')
        while isCorrect.upper() not in ['Y', 'N']:
          print('Invalid choice.')
          isCorrect = input('If results are valid, press \'Y\', else \'N\'')
        if isCorrect.upper() == 'Y':  #If flagged correct, increment n correct
          t.is_correct = True
          correct += 1
        else:
          t.is_correct = False
        n_test += 1
    accurate = 100 * correct / len(tests)
    if self.manual_evaluation == False and accurate < 100:  # Option to review for false negatives
      print(('%d tests completed with an accuracy of %d%%.') % (len(tests),
                                                                accurate))
      review = input(
          'Do you wish to review failed tests for false negatives? [Y/N]')
      if review.upper() == 'Y':
        for t in failed_tests:
          q = db.session.query(TestQuery).filter(
              TestQuery.query_id == t.query_id).first()
          print(('Query #%d: %r') % (n_test, q.query_text))
          print(('Results Expected: %r') % (q.results_expected))
          print(('Results: %r') % (t.result))
          isCorrect = input('Are results valid? [Y/N]')
          if isCorrect.upper() == Y:  #If flagged correct, increment n correct
            t.is_correct = True
            correct += 1
        accurate = 100 * correct / len(tests)  #If any change
    self.accuracy = accurate

  def __repr__(self):
    n_tests = len(
        db.session.query(TestResult).filter(
            TestResult.report_id == self.report_id).all())
    if self.accuracy >= 70:
      color = 'green'
    elif self.accuracy >= 50:
      color = 'yellow'
    else:
      color = 'red'
    out = 'Report: %d | Completed on: %s | Manually Completed: %s | Tests Run: %d | ' % (
        self.report_id, self.date, self.manual_evaluation, n_tests)
    accuracy = 'Accuracy: %r%%' % (self.accuracy)
    out = colored(out, 'blue') + colored(accuracy, color)
    return out