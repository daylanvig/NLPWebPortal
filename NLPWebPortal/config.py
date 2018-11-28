import os


SECRET_KEY = os.urandom(24) or 'BSAr3cVyZ4sarkAX' #Env or random pass
BASE = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.join(BASE, 'fileServer')
UPLOAD_DIR = os.path.join(BASE_DIR, "Uploads/")
MODEL_DIR = os.path.join(BASE_DIR, "LanguageModels/")
SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(BASE_DIR, 'database.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)
if not os.path.exists(UPLOAD_DIR): #Test if the directory exists or make it if it doesn't
    os.mkdir(UPLOAD_DIR)
