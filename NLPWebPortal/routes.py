from sqlalchemy import exc
from NLPWebPortal import app, db, login_manager, \
    render_template, redirect, request, session, url_for, flash,\
    login_user, logout_user, current_user, login_required, LoginManager,\
    SQLAlchemy, os
from NLPWebPortal.model import User, TrainingFile
from NLPWebPortal.interpreter import generate_weights
from datetime import datetime
from flask import jsonify
from werkzeug.utils import secure_filename


@app.route('/')
@app.route('/index')
def index():
  generate_weights()
  return render_template('index.html')


@app.route('/query', methods=['POST'])
def query():
  data = request.json
  query_text = data['query_text']
  private_check = data['private_check']

  return jsonify("HelloWorld")  ##TODO return the response


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'GET':
    return render_template('register.html')

  existing_user = User.query.filter_by(email=request.form['email']).first()
  if existing_user:
    flash("Error: Email in use", 'error')  ##Verify this
    return redirect(url_for('register'))
  else:
    user = User(request.form['email'], request.form['password'])
    db.session.add(user)
    db.session.commit()
    flash("Success. Please sign in.")
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
  if request.method == 'GET':
    return render_template('login.html')

  email = request.form['email']
  password = request.form['password']

  #Choose to remain logged in
  remember_me = False
  if 'remember_me' in request.form:
    remember_me = True

  registered_user = User.query.filter_by(email=email).first()

  #Verify password, log, redirect
  if (registered_user.check_password(password)):
    login_user(registered_user, remember=remember_me)
    registered_user.last_seen = datetime.utcnow
    return redirect(request.args.get('next') or url_for('index'))
  else:
    flash("Error: Invalid Credentials")

  return redirect(url_for('login'))


@app.route("/logout")
@login_required
def logOut():
  logout_user()
  flash('Successfully logged out.')
  return redirect(url_for('index'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
  if request.method == 'GET':
    return render_template('account.html')

  user = User.query.get(current_user.get_id())
  password = request.form['password']

  if 'deletebtn' in request.form:  #delete account form submitted
    if (user.check_password(password)):  #password authenticated
      logout_user()
      db.session.delete(user)
      db.session.commit()
      return redirect(url_for('login'))
    else:
      flash("Error, invalid password")

  return redirect(url_for('account'))


@app.route("/fileUpload", methods=["GET", "POST"])
@login_required
def fileUpload():
  if request.method == 'GET':
    return render_template('fileUpload.html')

  file = request.files['file']
  fn = secure_filename(file.filename)
  fileMeta = fn.split('.')

  #Metadata for file uploads
  new_file = TrainingFile(current_user.get_id(), fileMeta[-2], fileMeta[-1])
  db.session.add(new_file)
  db.session.commit()

  #This saves the file by the PKey, ensuring it's name is unique
  #Extension is kept
  file.filename = str(new_file.get_id()) + '.' + fileMeta[-1]  #File extension
  file.save(os.path.join(app.config['UPLOAD_DIR'], file.filename))
  return jsonify(success=True)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)


if __name__ == '__main__':
  app.run()
