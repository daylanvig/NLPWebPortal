from flask import Flask, redirect, render_template, request, session, url_for
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from NLPWebPortal import app, db, login_manager
from NLPWebPortal.model import User


@app.route('/') #route() is flasks way of directing the argument to the function(ie / leads to here)
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['email'], request.form['password'])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['email']
    password = request.form['password']
    registered_user = User.query.filter_by(email=email,password=password).first()
    if registered_user is None:
        flash('Email or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    return redirect(request.args.get('next') or url_for('index'))

@app.route("/logout")
def logOut():
    logout_user()
    return redirect(url_for('index'))

@app.route("/account")
def account():
    return render_template('account.html')     

@app.route("/fileUpload", methods=["GET", "POST"])
def fileUpload():
    return render_template('fileUpload.html')

if __name__ == '__main__':
    app.run()
