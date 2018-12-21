import os
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config.from_pyfile('config.py')
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Imports
from NLPWebPortal.model import User, TrainingFile, Dictionary, UserQuery, TestQuery
from NLPWebPortal.interpreter import interpret_query
from NLPWebPortal.form import LoginForm, RegisterForm
import NLPWebPortal.routes
import NLPWebPortal.neuralNetwork

#initialize database
db.create_all()

__all__ = [
    'render_template', 'redirect', 'request', 'session', 'url_for', 'flash',
    'SQLAlchemy', 'login_user', 'logout_user', 'current_user', 'login_required',
    'LoginManager', 'os', 'app', 'db', 'login_manager', 'interpret_query',
    'User', 'TrainingFile', 'Dictionary', 'UserQuery', 'TestQuery', 'LoginForm',
    'RegisterForm'
]