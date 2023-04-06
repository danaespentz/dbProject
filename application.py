#https://www.tutorialspoint.com/flask/flask_sessions.htm
import os, requests, string

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = os.urandom(24)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Create the Session object by passing it the application
#Important: firstly i set up the "app" and then i do Session(app)
Session(app)

# Set up database
#An engine is a common interface from sqlalchemy
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    if 'user_name' in session:
        user_name = session['user_name']
        return redirect(url_for('home', user_name=user_name))
    return redirect(url_for('login'))

#wherever I can divide each function in GET and POST I do it.
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_name = request.form.get("user_name")
        submitted_user_password = request.form.get("submitted_user_password")
        #fetchone() gives me the whole entry in the database [user_id, user_name, user_password]
        #in order to get just one, I have to select it with the dot operand
        user = db.execute("SELECT * from users WHERE user_name=:user_name",
                            {"user_name": user_name}).fetchone()
        #if user doesnt exist render login page again
        if user is None:
            return redirect(url_for('index'))
        user_password = user.user_password
        #check for correct password
        if user_password == submitted_user_password:
            session['user_name'] = user_name
        return redirect(url_for('index'))

#arguments are passed as part of the url or as post requests from forms
#or get requests with request.args.get without adding them in the url
@app.route('/<user_name>', methods = ['GET', 'POST'])
def home(user_name):
    if request.method == 'GET':
        if 'user_name' in session:
            return render_template('home.html', user_name=user_name)
        else:
            return redirect(url_for('index'))
    else:
        key = int(request.form.get('key'))
        return redirect(url_for('search_results', user_name=user_name, key=key))

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user_name', None)
   return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        #get form information
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        #Add user
        db.execute("INSERT INTO users (user_name, user_password) VALUES (:user_name, :user_password)",
                    {"user_name": user_name, "user_password": user_password})
        db.commit()
        return render_template("success.html")

if __name__ == "__main__":
    app.run()