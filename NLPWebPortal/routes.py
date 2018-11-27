from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from NLPWebPortal import app, db, login_manager
from NLPWebPortal.model import User
from datetime import datetime
from werkzeug.utils import secure_filename

@app.route('/') #route() is flasks way of directing the argument to the function(ie / leads to here)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    existing_user = User.query.filter_by(email=request.form['email']).first()
    if existing_user:
        flash("Error: Email in use", 'error') ##Verify this
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
    if(registered_user.check_password(password)):
        login_user(registered_user, remember = remember_me)
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

    if 'deletebtn' in request.form: #delete account form submitted
        if (user.check_password(password)): #password authenticated
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
    file.save(secure_filename(file.filename))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

if __name__ == '__main__':
    app.run()
