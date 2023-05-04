import os
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from myfaker import books

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sql'
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'mysecretkey'  # Set the secret key for Flask app
app.config['API_KEY'] = 'myapikey'  # Set an API key for the application
app.config['SESSION_TYPE'] = 'filesystem'

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    school_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __init__(self, user_name, user_password, name, school_name, role):
        self.user_name = user_name
        self.user_password = user_password
        self.name = name
        self.school_name = school_name
        self.role = role

class School(db.Model):
    school_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_name = db.Column(db.String(100), nullable=False)
    postcode = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    principal_name = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.String(100), nullable=False)

    def __init__(self, school_name, postcode, town, telephone, email, principal_name, admin_id):
        self.school_name = school_name
        self.postcode = postcode
        self.town = town
        self.telephone = telephone
        self.email = email
        self.principal_name = principal_name
        self.admin_id = admin_id

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(100))
    title = db.Column(db.String(100))
    authors = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    pages = db.Column(db.Integer)
    copies = db.Column(db.Integer)
    theme_categories = db.Column(db.String(100))
    language = db.Column(db.String(100))
    keywords = db.Column(db.String(100))
    cover_page = db.Column(db.String(100))

    def __init__(self, isbn, title, authors, publisher, pages, copies, theme_categories, language, keywords, cover_page):
        self.isbn = isbn
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.pages = pages
        self.copies = copies
        self.theme_categories = theme_categories
        self.language = language
        self.keywords = keywords
        self.cover_page = cover_page

class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Integer, nullable=False)
    issue = db.Column(db.String(100), nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['book_id'], ['book.book_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='RESTRICT', onupdate='CASCADE'),
    )

    def __init__(self, user_id, book_id, date, issue):
        self.user_id = user_id
        self.book_id = book_id
        self.date = date
        self.issue = issue

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(100))
    __table_args__ = (
        db.ForeignKeyConstraint(['book_id'], ['book.book_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='RESTRICT', onupdate='CASCADE'),
    )

    def __init__(self, user_id, book_id, rating, review_text=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.review_text = review_text

with app.app_context():
    db.create_all()

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
        user = User.query.filter_by(user_name=user_name, user_password=submitted_user_password).first()
        #if user doesnt exist render login page again
        if user:
            session['user_name'] = user_name
            return redirect(url_for('home', user_name=user_name))
        else:
            return render_template('login.html', error_message="Incorrect username or password.")


@app.route('/<user_name>/home', methods=['GET', 'POST'])
def home(user_name):
    if request.method == 'GET':
        if 'user_name' in session:
            return render_template('home.html', user_name=user_name)
        else:
            return redirect(url_for('index'))
    else:
        title = request.form.get("title")
        authors = request.form.get("authors")
        theme_categories = request.form.get("theme_categories")

        if not title and not authors and not theme_categories:
            return render_template('home.html', user_name=user_name, error_message="All fields are empty !")

        # Build the query dynamically based on the search parameters
        results = []
        for book in books:
            if title and title.lower() != book['title'].lower():
                continue
            if authors and authors.lower() != book['authors'].lower():
                continue
            if theme_categories and theme_categories.lower() != book['theme_categories'].lower():
                continue
            results.append(book)

        # Store the search results in the session
        session['results'] = results

        # Redirect to the search results page
        return redirect(url_for('search_results'))

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    # Retrieve the search results from the session
    results = session.get('results', [])
    if not results:
        return render_template('search_results.html', error_message="Not found.. Sorry")
    else:
        return render_template('search_results.html', results=results)

@app.route('/book_operations', methods = ['GET', 'POST'])
def book_operations():
        date = request.form.get("date")
        review_text = request.form.get("review_text")
        rating = request.form.get("rating")

        if not date and not rating:
            return render_template('book_operations.html', error_message="All fields are empty !")

        # Render the search results template with the results
        return render_template('book_operations.html', message="Your request was submitted successfully !")

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
        # get form information
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        name = request.form.get("name")
        role = request.form.get("role")
        school_name = request.form.get("school_name")
        if not user_name or not user_password or not name or not role or not school_name:
            return render_template('register.html', error_message="All fields are required !")

        new_user = User(user_name=user_name, user_password=user_password, name=name, school_name=school_name, role=role)
        db.session.add(new_user)
        db.session.commit()

        # redirect to the login page after successful registration
        return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == "__main__":
    app.run()