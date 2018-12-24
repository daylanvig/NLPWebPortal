import random
import string

from flask import jsonify
from sqlalchemy import exc, func
from werkzeug.utils import secure_filename

from NLPWebPortal import *


@app.route('/')
@app.route('/index')
@csrf.exempt
def index():
  """
  Called by Flask to load the index page where users can submit queries
  
  When users submit queries, they are handled via AJAX and directed to the query() method


  Returns:
    html template: HTML template containing a javscript text editor. If users are logged in
      they are able to select which database they wish to use(shared, private)
  """

  uid = current_user.get_id()
  try:
    file_exist = TrainingFile.query.filter_by(user_id=uid).first()
    uid = file_exist
  except:
    uid = None

  return render_template('index.html', uid=uid)


@app.route('/query', methods=['POST'])
@csrf.exempt
def query():
  """
  The method handles user query submissions
  
  When users submit queries on the index page, they arre handled via an AJAX post
  which directs to this method. This method provides for validation that the user is
  logged in (if they're requesting a private database) and directs the request to the
  interpreter. The result is returned in json form to the text editor.
  
  Returns:
    JSON: A json formatted string containing the results that were returned by the
    interpreter. 
  """

  # Accept the form and its information
  data = request.json
  query_text = data['query_text']
  private_check = data['private_check']
  curr_user = current_user.get_id()

  # If user wants private, they must be logged in
  if (private_check and not curr_user):
    raise Exception('Not logged in')
  else:
    return jsonify(interpret_query(curr_user, query_text, private_check))


@app.route('/update_account', methods=['POST'])
@login_required
@csrf.exempt
def update_account():
  """
  This method accepts an AJAX post to update account details.
  
  Users who update their account details(email, password) will have their request POST directed to here.
  After validating the form, the information will be validated and a JSON response returned to the client.
  
  Returns:
    JSON: Message to be be used in the ALERT statement to confirm the update or return an error.
  """

  # Get form
  data = request.json
  try:
    email = data['email']
  except:
    email = None
  password = data['password']

  user = User.query.filter_by(user_id=current_user.get_id()).first()
  if user.check_password(password):  #verify password
    if email:  #Update email
      try:
        user.email = email
        db.session.commit()
        return jsonify('Update successful')
      except:
        db.session.rollback()
        return jsonify('Email in use')
    else:  #Update password
      new_password = data['new_password']  # TODO Verify working
      if len(new_password) > 8:
        for c in new_password:
          if c.isalpha():
            has_letter = True
          if c.isdigit():
            has_number = True
          if has_letter and has_number:
            user.set_password(new_password)
            db.session.commit()
            return jsonify('Update successful')
      return jsonify(
          'Password does not meet minimum requirements: 8 characters, 1 alphabetic character(a-z, A-Z), 1 numeric digit(0-9)'
      )
  else:
    return jsonify('Error: Password does not match records')


@app.route('/register', methods=['GET', 'POST'])
def register():
  """
  Loads the account registration page
  
  Loads the template for the account registration page, asking the user to provide an email address
  and password, with password confirmation. Upon submitting the form, the system verifies the email is unique
  and then creates the account by adding the information to the database.
  
  Returns:
    html template: Redirect to the login page if successful, or the registration page if an error
      occurs. 
  """

  form = RegisterForm()
  if form.validate_on_submit():
    # Verify email is unique
    existing_user = User.query.filter_by(email=request.form['email']).first()

    if existing_user:  # Email in use
      flash("Error: Email in use", 'error')
      return redirect(url_for('register'))
    else:  # New email, make account
      user = User(request.form['email'], request.form['password'])
      try:
        db.session.add(user)
        db.session.commit()
      except:
        db.session.rollback()
      flash("Success. Please sign in.")
      return redirect(url_for('login'))

  return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
  """
  Flask redirect for the login page

  Loads the login page and prompts for email, password, with an option to be remembered
  If user has reset their password but has not set a new one, redirect to a page to set it instead.

  Returns:
    html template: The page the user attempted to go to (if it required login), otherwise the index page if successful
      If login fails, returns the login page again.
  """
  loginform = LoginForm()

  if loginform.validate_on_submit():
    email = loginform.email.data
    password = loginform.password.data
    remember_me = loginform.remember_check.data

    registered_user = User.query.filter(User.email.ilike(email)).first()
    #User exists
    if registered_user:
      #If password has been changed since reset,
      if registered_user.password_changed >= registered_user.password_reset:
        #Verify password, try to log in, redirect as needed
        if (registered_user.check_password(password)):
          login_user(registered_user, remember=remember_me)
          registered_user.last_seen = datetime.utcnow
          return redirect(request.args.get('next') or url_for('index'))
        else:
          flash("Error: Password does not match records.")
          return redirect(url_for('login', email=email))
        #Password reset
      else:
        flash('Password must be changed.')
        return redirect(url_for('reset', email=email, pw=password))
    else:
      flash('Error: Provided email address does not correspond to any records.')
      return redirect(url_for('login'))
  return render_template('login.html', loginform=loginform)


@app.route('/forgot_password', methods=['GET', 'POST'])
@csrf.exempt
def forgot_password():
  """
  Allows users to reset forgotten passwords
  
  If a user selects "forgot password" this page is loaded. The result is a form which prompts for the user's email address.
  If the email is valid a temporary password is generated and emailed to the user, after which they have 24 hours to login and reset it.
  
  Returns:
    html template: The login page html form if posted, else the forget.html form
  """

  if request.method == 'GET':
    return render_template('forgot.html')

  email = request.form['email']
  user = User.query.filter(User.email.ilike(email)).first()
  #If an email matches the database
  if user:
    temp_password = []
    #Creates a 13 character password
    n_num = random.randint(1, 5)
    n_char = 13 - n_num
    for i in range(n_num):  # Add numbers
      temp_password.append(random.choice(string.digits))
    for i in range(n_char):  # letters
      temp_password.append(random.choice(string.ascii_letters))
      #Order randomize
    random.shuffle(temp_password)
    #string it
    temp_password = ''.join(temp_password)
    print(temp_password)
    #save to database
    user.set_password(temp_password)
    user.password_reset = datetime.utcnow()
    db.session.commit()
    msg = Message(
        'Password Reset Request',
        sender='daylancapstoneproject@gmail.com',
        recipients=[email])
    body_text = "Your temporary password is:    %r \nPassword must be changed within 24 hours." % (
        temp_password)
    msg.body = body_text
    mail.send(msg)
  flash('Password reset if email matches any records. Check email to reset.')
  return redirect(url_for('login'))


@app.route('/reset', methods=['GET', 'POST'])
@csrf.exempt
def reset():
  """
  Loads the HTML template that lets a user enter a new password after theirs has been reset
  
  After a user attempts to log in with a temporary password, the login page redirects to here. The user can then create a new password.
  
  Returns:
    html template:
  """

  pw = request.args.get('pw')
  reset_form = ResetForm()
  #Post to update password
  if reset_form.validate_on_submit():
    email = request.form['email']
    password = reset_form.password.data
    user = User.query.filter(User.email.ilike(
        request.args.get('email'))).first()
    if user and user.check_password(pw):
      user.set_password(password)
      user.password_changed = datetime.utcnow()
      db.session.commit()
      flash('Success, please log in')
      return redirect(url_for('login'))
    else:  #This should not happen unless the user attempts to POST without using the form/accessing the page wrong
      flash(
          'Something went wrong, email does not exist or current password does not match'
      )
      return redirect(url_for('login'))
  else:
    user = User.query.filter(User.email.ilike(
        request.args.get('email'))).first()
    if pw and user.check_password(pw) and (
        user.password_reset + timedelta(hours=24) >= datetime.utcnow()):
      return render_template(
          'reset.html', email=user.email, form=reset_form, pw=pw)
    else:
      flash(
          'Something went wrong. Temporary password may have expired or does not match records.'
      )
      return redirect(url_for('login'))


@app.route("/logout")
@csrf.exempt
def logOut():
  """
  Logs the user out and redirects to the home page
  
  Logout functionality handled by flask_login. Statuses current_user as None, isAuthenticated as
    False
  
  Returns:
    html template: /index page
  """

  flash('Successfully logged out.')
  logout_user()
  return redirect(url_for('index'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
@csrf.exempt
def account():
  """
  Flask redirect for account history page

  If the user calls the /account page, method is called and returns their profile with history.
  Allows for profile updates or account deletion. 

  Returns:
    html template: The html template for the account page when called via GET, or redirect for the login page if the user POSTs to delete their account
  """

  uid = current_user.get_id()  #get user
  # Query the database for the user's files and queries.
  files = TrainingFile.query.filter_by(user_id=uid).all()
  queries = UserQuery.query.filter_by(user_id=uid).all()

  if request.method == 'GET':
    return render_template(
        'account.html', user=current_user, files=files, queries=queries)

  # If the user submits the delete form (ie POST request)
  user = User.query.get(uid)
  password = request.form['password']

  if 'deletebtn' in request.form:  #Verify delete was in form
    if (user.check_password(password)):  #Verify password
      logout_user()
      db.session.delete(user)
      db.session.commit()  #TODO Try to delete test files
      return redirect(url_for('login'))
    else:
      flash("Error, invalid password")
      return redirect(url_for('account'))


@app.route("/fileUpload", methods=["GET", "POST"])
@login_required
@csrf.exempt
def file_upload():
  """
  Flask redirect allowing users to upload files
  
  Loads the template to support file uploads via the get method. When users submit forms via POST, they
  are stored on the server and added to the database to reflect ownership.
  
  Returns:
    json dict: Confirmation that files have been uploaded 
  """

  if request.method == 'GET':
    return render_template('fileUpload.html')
  else:  # Receive files via AJAX
    types = ['txt', 'doc']
    file_up = request.files.listvalues()
    for file_store in file_up:
      for f in file_store:
        fn = secure_filename(f.filename)
        fileMeta = fn.split('.')
        if fileMeta[-1] not in types:
          raise Exception  #invalid file type

        #Metadata for file uploads
        new_file = TrainingFile(current_user.get_id(), fileMeta[-2],
                                fileMeta[-1])
        db.session.add(new_file)
        db.session.commit()

        #This saves the file by the PKey, ensuring it's name is unique
        #Extension is kept
        f.filename = str(
            new_file.get_id()) + '.' + fileMeta[-1]  #File extension
        f.save(os.path.join(app.config['UPLOAD_DIR'], f.filename))
    return jsonify(success=True)


@login_manager.user_loader
def load_user(user_id):
  """
  Loads the current user, required by flask_login
  
  
  Args:
    user_id (int): user id number
  
  Returns:
    User: User in database who matches the user_id
  """

  return User.query.get(user_id)


if __name__ == '__main__':
  app.run(host='0.0.0.0')
