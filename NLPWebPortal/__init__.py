import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = os.urandom(24) or 'BSAr3cVyZ4sarkAX' #Env or random pass


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app) ##TODO CONFIG DB22
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#Imports
import NLPWebPortal.routes
import NLPWebPortal.model

db.create_all()

@login_manager.user_loader
def load_user(id):
    return user.User.query.get(int(id))
