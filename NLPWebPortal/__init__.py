import os
from flask import Flask, render_template, redirect, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Imports
import NLPWebPortal.model
import NLPWebPortal.routes
import NLPWebPortal.interpreter
import NLPWebPortal.neuralNetwork

#initialize database
db.create_all()
