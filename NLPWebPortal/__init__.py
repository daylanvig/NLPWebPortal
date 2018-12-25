import os
import sys
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer
from datetime import date, datetime, timedelta

#Config
app = Flask(__name__)
app.config.from_pyfile('config.py')
csrf = CSRFProtect(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

#Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Imports
from NLPWebPortal.model import User, TrainingFile, Dictionary, UserQuery, TestQuery
from NLPWebPortal.languageModel import LanguageModel
from NLPWebPortal.interpreter import interpret_query
from NLPWebPortal.form import LoginForm, RegisterForm, ResetForm
import NLPWebPortal.routes

#initialize database
db.create_all()

__all__ = [
    'render_template', 'redirect', 'request', 'session', 'url_for', 'flash',
    'SQLAlchemy', 'login_user', 'logout_user', 'current_user', 'login_required',
    'LoginManager', 'os', 'sys', 'app', 'db', 'login_manager',
    'interpret_query', 'User', 'TrainingFile', 'Dictionary', 'UserQuery',
    'TestQuery', 'LoginForm', 'RegisterForm', 'LanguageModel', 'mail',
    'Message', 'Mail', 'ResetForm', 'date', 'datetime', 'timedelta'
]