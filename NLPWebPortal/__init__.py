import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = os.urandom(24) or 'BSAr3cVyZ4sarkAX' #Env or random pass

#Database setup 
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app) 
migrate = Migrate(app, db)


#Login manager configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Imports
import NLPWebPortal.routes
import NLPWebPortal.model
import NLPWebPortal.accountHelper

#initialize database
db.create_all()
