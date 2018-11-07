from flask import Flask, render_template, request, redirect

app = Flask(__name__) #create website in variable called app

email_addresses = []

#@ is decorator, it creates function definition
@app.route('/') #route() is flasks way of directing the argument to the function(ie / leads to here)
def homePage():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()

