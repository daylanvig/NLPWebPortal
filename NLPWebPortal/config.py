import os

SECRET_KEY = os.urandom(24) or 'BSAr3cVyZ4sarkAX'  #Env or random pass

#Directories--
BASE = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.join(BASE, 'FileServer')
UPLOAD_DIR = os.path.join(BASE_DIR, "TrainingFiles")
MODEL_DIR = os.path.join(BASE_DIR, "LanguageModels")
REPORT_DIR = os.path.join(BASE_DIR, "Reports")
#----------------------------------------

#Database--
SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(BASE_DIR, 'database.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

#Mail setup--
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'daylancapstoneproject@gmail.com'
MAIL_PASSWORD = 'fymozvjwfvfebdvs'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

#Test if the directory exists or make it if it doesn't
if not os.path.exists(BASE_DIR):
  os.mkdir(BASE_DIR)
if not os.path.exists(UPLOAD_DIR):
  os.mkdir(UPLOAD_DIR)
if not os.path.exists(MODEL_DIR):
  os.mkdir(MODEL_DIR)
