import os
from NLPWebPortal import app
from NLPWebPortal.model import db, User, TrainingFile


#Opens the file, reads its contents
def load_file(file_name):

    selected_file = False

    #Checks for encoding types
    try:
        selected_file = open(os.path.join(app.config['UPLOAD_DIR'], file_name), 'rt') 
    except:
        selected_file = open(os.path.join(app.config['UPLOAD_DIR'], file_name), 'rt', encoding='utf8')
    
    file_text = selected_file.read()
    selected_file.close()

    return file_text.split() #Returns all the words in the file

#File cleaning procedure
def clean_file(file_contents):

    words = [word.lower() for word in file_contents] #lower case
    #TODO Clean file
    #TODO Write change to disk
    #TODO Update database to flag as clean
    return ("This would be file contents")



#------------------------------------------------------------------------------------------Main Code _-----#

#Selects all the files not flagged as cleaned and puts into a list
files_to_clean = TrainingFile.query.filter(TrainingFile.cleaned == False).all()

for file in files_to_clean:
    if file.name() == "3.txt":
        file_contents = load_file(file.name())
        cleaned_text = clean_file(file_contents)
        print(cleaned_text)
    
    print ("no")
    
