from config import MODEL_DIR, BASE_DIR, SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, query
from model import User, TrainingFile

#connect to database
engine = create_engine(SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

to_be_cleaned = [] #list of files to be cleaned

for x in session.query(TrainingFile):
    print (x.file_name)