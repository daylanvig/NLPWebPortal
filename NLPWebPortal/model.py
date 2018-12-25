from flask_sqlalchemy import SQLAlchemy
from termcolor import colored
from werkzeug.security import check_password_hash, generate_password_hash

from . import date, datetime, db


class User(db.Model):
  """
  User account information
  
  Creates the database table that holds the account information for user accounts.
  Maintains information such as password reset/change time and files owned/submitted to control access.
  
  Args:
    email (String): The email address used to register
    password (String): The user's requested password. This will be hashed and the hash will be stored, the plain text password will not.
  
  """

  __tablename__ = 'user'

  user_id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(50), unique=True, index=True)
  pw_hash = db.Column(db.String)
  registered_on = db.Column(db.DateTime)
  last_seen = db.Column(db.DateTime)
  training = db.relationship('TrainingFile', backref='user', lazy=True)
  password_reset = db.Column(db.DateTime)
  password_changed = db.Column(db.DateTime)

  def __init__(self, email, password):
    self.email = email
    self.set_password(password)
    self.registered_on = datetime.utcnow()
    self.password_reset = datetime.utcnow()
    self.password_changed = datetime.utcnow()

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
  """
  Training file meta deta 
  
  When users uploaded files for the language model to be trained off of, the meta information is stored.

  
  Args:
    user_id (int): The ID number of the user who uploaded the file.
    file_name (string): The file's original name - The file will be stored on disk under a new name
    extension (string): The extension of the uploaded file.
  
  """

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
  """
  Dictionary holding words found in the input data and their frequency/count
  
  Each time a word is found in a file its count is incremented. Stored words are later accessed when the interpreter identifies a word that is
  missing characters.
  
  Args:
    word (String): The word
    count (int): Number of times the word has been in training data

  """

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
  """
   Base query, accessed by/extended by UserQuery and TestQuery
   
  """

  __tablename__ = 'query'

  query_id = db.Column(db.Integer, primary_key=True)
  query_text = db.Column(db.Text, nullable=False)
  type = db.Column(db.String(50))

  __mapper_args__ = {'polymorphic_identity': 'query', 'polymorphic_on': 'type'}

  def __init__(self, query):
    self.query_text = query


class UserQuery(Query):
  """
  UserQueries represent queries which have been submitted by logged in users.
  
  When a valid user submits a query, the results are stored here so that they can be accessed by the account method so that users can view their history
  
  Args:
    query (String): The raw fragmented query
    user_id (int): The ID number of the user who submitted the query
    use_private (Boolean): True if the user requested to use their private database, else False
    result (String): The result returned by the interpreter
  """

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
  """
  TestQuery objects are used to store sample tests which can be run by a system admin to monitor the quality of the results being returned by the model so that
  it can be adjusted
  
  When a user accesses the admin system, they can choose to add test queries (requiring the raw query text and expected results)
  These TestQueries are later accessed when tests are run to compare actual results.
  
  Args:
    query (String): Fragmented query, must represent missing information using _<C>_, _<W>_, _<S>_

  """

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
  """
  Represents a completed test, created using a test query and the current language model

  When a report is created, testResult objects are created to represent each individual query. Input data is received from TestQuery, results are stored here. 

  Args:
    query_id (int): The id number of a TestQuery object
    result (String): Completed string as returned by the interpreter
    report_id (int): Report number that this test belongs to

  """

  test_id = db.Column(db.Integer, primary_key=True)
  query_id = db.Column(
      db.Integer, db.ForeignKey('test_query.query_id'), nullable=False)
  report_id = db.Column(
      db.Integer, db.ForeignKey('report.report_id'), nullable=False)
  result = db.Column(db.Text)
  is_correct = db.Column(db.Boolean)

  def __init__(self, query_id, report_id, result):
    self.query_id = query_id
    self.result = result
    self.report_id = report_id


class Report(db.Model):
  """
  Creates a report of query accuracy
  
  Report used to hold summary data of test queries. The associated TestResult objects represent individual tests.

  Args: 
    manual (Boolean): True if the user chose to manually evaluate the test results(preferred), otherwise False.

  Returns:
    String: Colored output string depending on the results
  """

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
    """
      Represents the summary of the report with colored text depending on the quality of the tests.
    """

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
