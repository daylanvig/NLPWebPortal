import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, logout_user, current_user, login_required, LoginManager

app = Flask(__name__)
app.secret_key = os.urandom(24) or 'BSAr3cVyZ4sarkAX' #Env or random pass

db = SQLAlchemy(app) ##TODO CONFIG DB
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
