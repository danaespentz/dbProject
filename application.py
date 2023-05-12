import os, datetime
from datetime import date, timedelta, timezone
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
    age = db.Column(db.Integer, nullable=False)
    school_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def __init__(self, user_name, user_password, name, age, school_name, role):
        self.user_name = user_name
        self.user_password = user_password
        self.name = name
        self.age = age
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
        self.authors = ", ".join(authors)
        self.publisher = publisher
        self.pages = pages
        self.copies = copies
        self.theme_categories = ", ".join(theme_categories)
        self.language = language
        self.keywords = ", ".join(keywords)
        self.cover_page = cover_page

def dict_Book(book):
    return {
        "book_id": book.book_id,
        "isbn": book.isbn,
        "title": book.title,
        "authors": book.authors.split(','),
        "publisher": book.publisher,
        "pages": book.pages,
        "copies": book.copies,
        "theme_categories": book.theme_categories.split(','),
        "language": book.language,
        "keywords": book.keywords.split(','),
        "cover_page": book.cover_page
    }


class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today, nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    issue = db.Column(db.String(100), nullable=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['book_id'], ['book.book_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='RESTRICT', onupdate='CASCADE'),
    )

    def __init__(self, user_id, book_id, title, issue_date, issue):
        self.user_id = user_id
        self.book_id = book_id
        self.title = title
        self.issue_date = issue_date
        self.issue = issue

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.String(100))
    mode = db.Column(db.Boolean, default=False)
    __table_args__ = (
        db.ForeignKeyConstraint(['book_id'], ['book.book_id'], ondelete='RESTRICT', onupdate='CASCADE'),
        db.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='RESTRICT', onupdate='CASCADE'),
    )

    def __init__(self, user_id, book_id, rating, mode, review_text=None):
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.review_text = review_text
        self.mode = mode

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
            session['user_id'] = user.user_id
            return redirect(url_for('home', user_name=user_name))
        else:
            return render_template('login.html', error_message="Incorrect username or password.")

@app.route('/my_profile/', methods=['GET', 'POST'])
def my_profile():
    user_name = session['user_name']
    user = User.query.filter_by(user_name=user_name).first()
    if request.method == 'POST':
        if request.form['submit_button'] == 'modify':
            # code to modify user details
            pass
        elif request.form['submit_button'] == 'Remove':
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('myprofile.html', user=user)

@app.route('/<user_name>/home', methods=['GET', 'POST'])
def home(user_name):
    if request.method == 'GET':
        if 'user_name' in session:
            db.session.add_all([Book(**book) for book in books])
            db.session.commit()
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
        if title:
            search = Book.query.filter_by(title=title).all()
        if authors:
            search = Book.query.filter_by(authors=authors).all()
        if theme_categories:
            search = Book.query.filter_by(theme_categories=theme_categories).all()
        if search:
            results = [dict_Book(book) for book in search]

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

@app.route('/my_issues')
def my_issues():
    # Retrieve the user's issues from the database
    user_borrowings = db.session.query(Report).filter_by(user_id=session['user_id'], issue='borrowed').all()
    user_reservations = db.session.query(Report).filter_by(user_id=session['user_id'], issue='reserved').all()
    
    if not user_borrowings and not user_reservations:
        return render_template('my_issues.html', message="No Reports")

    return render_template('my_issues.html', user_reservations=user_reservations, user_borrowings=user_borrowings)

@app.route('/cancel_issue', methods=['GET', 'POST'])
def cancel_issue():
    report_id = request.args.get('issue_id')
    message='Not allowed'
    # Delete the issue with the given ID from the database
    if report_id:
        report = Report.query.filter_by(report_id=report_id).first()
        db.session.delete(report)
        db.session.commit()
        message = 'Reservation cancelled successfully.'    
    return redirect(url_for('my_issues'))

@app.route('/book_operations', methods=['GET', 'POST'])
def book_operations():
    if request.method == 'GET':
        isbn = request.args.get('isbn')
        
        book = Book.query.filter_by(isbn=isbn).first()
        book_dict = dict_Book(book)
        book_id = book_dict['book_id']
        title = book_dict['title']
        copies = book_dict['copies']
        
        session['book_id'] = book_id
        session['title'] = title
        session['copies'] = copies
        
        reviews = Rating.query.filter_by(book_id=book_id).all()
        return render_template('book_operations.html', reviews=reviews)
    else:
        issue_date = request.form.get("date")
        review_text = request.form.get("review_text")
        rating = request.form.get("rating")
        user_id = session['user_id']
        
        book_id = session['book_id']
        title = session['title']
        copies = session['copies']

        # Check if the user is a student or professor
        user = User.query.filter_by(user_id=user_id).first()
        role = user.role

        if not issue_date and not rating and not review_text:
            return render_template('book_operations.html', message="All fields are empty !")

        if rating and review_text:
            if role == 'student':
                new_rating = Rating(user_id=user_id, book_id=book_id, rating=rating, review_text=review_text, mode=False)
                db.session.add(new_rating)
                db.session.commit()
                return render_template('book_operations.html', message="Your rating and review requests were submitted successfully !")
            if role == 'professor':
                new_rating = Rating(user_id=user_id, book_id=book_id, rating=rating, review_text=review_text, mode=True)
                db.session.add(new_rating)
                db.session.commit()
                return render_template('book_operations.html', message="Your rating and review were submitted successfully !")

        if rating:
            new_rating = Rating(user_id=user_id, book_id=book_id, rating=rating, review_text='', mode=True)
            db.session.add(new_rating)
            db.session.commit()
            return render_template('book_operations.html', message="Your rating was submitted successfully !")

        if review_text:
            if role == 'student':
                new_review = Rating(user_id=user_id, book_id=book_id, rating=0, review_text=review_text, mode=False)
                db.session.add(new_review)
                db.session.commit()
                return render_template('book_operations.html', message="Your review request was submitted successfully !")
            if role == 'professor':
                new_review = Rating(user_id=user_id, book_id=book_id, rating=0, review_text=review_text, mode=True)
                db.session.add(new_review)
                db.session.commit()
                return render_template('book_operations.html', message="Your review was submitted successfully !")

        if issue_date:
            borrowed = Report.query.filter_by(book_id=book_id, user_id=user_id, issue="borrowed").first()
            if borrowed:
                return render_template('book_operations.html', message="Before you reserve another copy of this book you have to return yours. ")
            # Calculate the start and end dates of the current week
            date = datetime.datetime.strptime(issue_date, '%Y-%m-%d').date()
            today = date.today()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Cancel any expired reservations
            expired_reservations = Report.query \
            .filter_by(book_id=book_id) \
            .filter(Report.issue_date <= datetime.datetime.utcnow() - timedelta(days=7)) \
            .filter(Report.issue == "reserved") \
            .all()

            for reservation in expired_reservations:
                db.session.delete(reservation)
            
            reports_this_week = Report.query \
            .filter_by(user_id=user_id) \
            .filter(Report.date >= start_of_week) \
            .filter(Report.date <= end_of_week) \
            .all()
            
            num_books_this_week = sum(1 for r in reports_this_week)
            # Check if the user has exceeded the borrowing limit for this week
            if role == 'student' and num_books_this_week >= 2:
                return render_template('book_operations.html', message="You have already reserved 2 books this week!")
            elif role == 'professor' and num_books_this_week >= 1:
                return render_template('book_operations.html', message="You have already reserved 1 book this week!")
            if copies == 0:
                new_reservation = Report(user_id=user_id, book_id=book_id, title=title, issue_date=date, issue="onhold")
                db.session.add(new_reservation)                
                db.session.commit()
                return render_template('book_operations.html', message="There are no copies of this book left .. Your are in the waiting list!")
            
            new_reservation = Report(user_id=user_id, book_id=book_id, title=title, issue_date=date, issue="reserved")
            db.session.add(new_reservation)                
            db.session.commit()
            return render_template('book_operations.html', message="Your reservation request was submitted successfully !")    
        return render_template('book_operations.html', message="Error")    

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
        age = request.form.get("age")
        role = request.form.get("role")
        school_name = request.form.get("school_name")
        if not user_name or not user_password or not name or not age or not role or not school_name:
            return render_template('register.html', error_message="All fields are required !")

        new_user = User(user_name=user_name, user_password=user_password, name=name, age=age, school_name=school_name, role=role)
        db.session.add(new_user)
        db.session.commit()

        # redirect to the login page after successful registration
        return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == "__main__":
    app.run()