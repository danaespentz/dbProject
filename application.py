import os, datetime, random
from datetime import date, timedelta, timezone
from flask import Flask, session, render_template, request, redirect, url_for, jsonify, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from myfaker import books
import sqlite3

# Connect to the database or create it if it doesn't exist
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # Set the secret key for Flask app
app.config['API_KEY'] = 'myapikey'  # Set an API key for the application
app.config['SESSION_TYPE'] = 'filesystem'

@app.route("/")
def index():
    if 'user_name' in session:
        user_name = session['user_name']
        return redirect(url_for('home', user_name=user_name))
    return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_name = request.form.get("user_name")
        submitted_user_password = request.form.get("submitted_user_password")
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name=? AND user_password=?", (user_name, submitted_user_password))
        user = cursor.fetchone()
        
        if user:
            if user[7]==False:
                return render_template('login.html', error_message="You are not approved yet!")
            session['user_name'] = user_name
            session['user'] = user
            return redirect(url_for('home', user_name=user_name))
        else:
            return render_template('login.html', error_message="Incorrect username or password.")

@app.route('/my_profile', methods=['GET', 'POST'])
def my_profile():
    if request.method == 'POST':
        if request.form['submit_button'] == 'modify':
            # code to modify user details
            pass
        elif request.form['submit_button'] == 'Remove':
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (session['user'][0],))
            return redirect(url_for('login'))
    return render_template('myprofile.html', role = session['user'][6], user_name = session['user'][1], user=session['user'])

@app.route('/<user_name>/home', methods=['GET', 'POST'])
def home(user_name):
    if request.method == 'GET':
        if 'user_name' in session:
            return render_template('home.html', user_name=user_name, role = session['user'][6])
        else:
            return redirect(url_for('index'))
    else:
        title = request.form.get("title")
        authors = request.form.get("authors")
        theme_categories = request.form.get("theme_categories")
        copies = request.form.get("copies")
        if not title and not authors and not theme_categories and not copies:
            return render_template('home.html', user_name=user_name, role = session['user'][6], error_message="All fields are empty !")

        if title:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books WHERE title=?", (title,))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message = "There is no book with this title!")
        if authors:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT * FROM books WHERE authors LIKE ? """, (f'%{authors}%',))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message = "There are no books by this author!")
        if theme_categories:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT * FROM books WHERE theme_categories LIKE ? """, (f'%{theme_categories}%',))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message="Book Categories are: Fiction, Non-Fiction, Mystery, Thriller, Biography, History, Science Fiction, Romance, Cooking, Poetry. It is important to spell them correctly!")
        if copies:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books WHERE copies=?", (copies,))
            results = cursor.fetchall()

        # Store the search results in the session
        session['results'] = results

        # Redirect to the search results page
        return redirect(url_for('search_results'))

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    user_name = session['user_name']
    # Retrieve the search results from the session
    results = session.get('results', [])
    if not results:
        return render_template('search_results.html', user_name=user_name, role = session['user'][6], error_message="Not found.. Sorry")
    else:
        return render_template('search_results.html', user_name=user_name, role = session['user'][6], results=results)

@app.route('/lateBorrowings', methods=['GET', 'POST'])
def lateBorrowings():
    if request.method == 'GET':
        user_name = session['user_name']
        return render_template('lateBorrowings.html', user_name=user_name, role = session['user'][6])
    else:
        user_name = session['user_name']
        name = request.form.get("name")
        latedays = request.form.get("latedays")

        if not name and not latedays:
            return render_template('lateBorrowings.html', user_name=user_name, role = session['user'][6], error_message="All fields are empty !")
        
        today = datetime.date.today()
        r = []
        borrow_results = []
        if name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE name=?", (name,))
            user = cursor.fetchone()
            user_id = user[0]
        if name and latedays:    
            try:
                days = int(latedays)
            except ValueError:
                return render_template('lateBorrowings.html', user_name=user_name, role = session['user'][6], error_message="Invalid number of days!")
            issue_date = today - datetime.timedelta(days=days)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM reports
                WHERE user_id = ? AND issue_date = ? AND issue = 'borrowed'
                """, (user_id, issue_date))
            search = cursor.fetchall()        
        if name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM reports
                WHERE user_id = ? AND issue = 'borrowed'
                """, (user_id,))
            search = cursor.fetchall()    
            if search:
                for result in search:
                    issue_date = datetime.datetime.strptime(result[5], '%Y-%m-%d').date()
                    days = (today - issue_date).days
                    if days > 0:
                        result[5] = issue_date.strftime('%a, %d %b %Y')
                        borrow_results.append(result)
        if latedays:
            try:
                days = int(latedays)
            except ValueError:
                return render_template('lateBorrowings.html', user_name=user_name, role = session['user'][6], error_message="Invalid number of days!")
            issue_date = today - datetime.timedelta(days=days)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM reports
                WHERE issue_date = ? AND issue = 'borrowed'
                """, (issue_date,))
            borrow_results = cursor.fetchall()   
        if borrow_results:   
            session['borrow_results'] = borrow_results
            session['days'] = days
        
        return redirect(url_for('search_borrowings'))

@app.route('/search_borrowings', methods=['GET', 'POST'])
def search_borrowings():
    user_name = session['user_name']
    # Retrieve the search results from the session
    borrow_results = session.get('borrow_results', [])
    days = session.get('days')
    if not days:
        days=0
    if not borrow_results:
        return render_template('search_borrowings.html', user_name=user_name, role = session['user'][6], error_message="Not found.. Sorry")
    else:
        return render_template('search_borrowings.html', user_name=user_name, role = session['user'][6], days=abs(days), results=borrow_results)

@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
    if request.method == 'GET':
        user_name = session['user_name']
        return render_template('ratings.html', user_name=user_name)
    else:
        user_name = session['user_name']
        by_user = request.form.get("by_user")
        by_category = request.form.get("by_category")

        if not by_user and not by_category:
            return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="All fields are empty !")
    
        # Build the query dynamically based on the search parameters
        results = []
        if by_user:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE name=?", (by_user,))
            user = cursor.fetchone()
            if not user:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="There is no student with this name")
            user_id = user[0]
        if by_category and by_user:
            MO = 0
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT *
                    FROM books
                    WHERE theme_categories LIKE ?
                """, (f'%{by_category}%',))
            search = cursor.fetchall()    
            if search:
                count = 0 
                for book in search:
                    book_id = book[0]
                    with sqlite3.connect('database.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT *
                            FROM ratings
                            WHERE book_id = ? AND user_id = ?
                        """, (book_id, user_id))
                    ratings = cursor.fetchall()
                    if ratings:
                        for result in ratings:
                            count = count + 1
                            MO = MO + result[4]
                if count:
                    MO = MO/count 
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], category = by_category, name = by_user, MO=MO)
            else:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="Incorrect Book category")
        if by_user:
            MO = 0
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT *
                    FROM ratings
                    WHERE user_id = ?
                """, (user_id,))
            search = cursor.fetchall()
            if search:
                count = 0 
                for result in search:
                    count = count + 1
                    MO = MO + int(result[4])
                if count:
                    MO = MO/count 
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], name = by_user, MO=MO)
        if by_category:
            count = 0
            MO = 0
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT *
                    FROM books
                    WHERE theme_categories LIKE ?
                """, (f'%{by_category}%',))
            search = cursor.fetchall()
            if search:
                for book in search:
                    book_id = book[0]
                    with sqlite3.connect('database.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT *
                            FROM ratings
                            WHERE book_id = ? """, (book_id,))
                    ratings = cursor.fetchall()
                    if ratings:
                        for result in ratings:
                            count = count + 1
                            MO = MO + result[4]
                if count:
                    MO = MO/count 
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], category = by_category, MO=MO)
            else:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="Incorrect Book category")
        return render_template('ratings.html', user_name=user_name, role = session['user'][6])

@app.route('/my_issues',methods=['GET', 'POST'])
def my_issues():
    user_name = session['user_name']
    if user_name == "school_admin":
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            user_borrowings = cursor.execute("SELECT * FROM reports WHERE issue='borrowed'").fetchall()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            user_reservations = cursor.execute("SELECT * FROM reports WHERE issue='reserved'").fetchall()
        
        rating_id = request.args.get('rating_id')
        if rating_id:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE ratings SET mode=1 WHERE rating_id=?", (rating_id,))
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            rating_approvals = cursor.execute("SELECT * FROM ratings WHERE mode=0").fetchall()
        return render_template('my_issues.html', user_name=user_name, role = session['user'][6], user_reservations=user_reservations, user_borrowings=user_borrowings, rating_approvals=rating_approvals)
    else:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            user_borrowings = cursor.execute("SELECT * FROM reports WHERE user_id=? AND issue='borrowed'", (session['user'][0],)).fetchall()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            user_reservations = cursor.execute("SELECT * FROM reports WHERE user_id=? AND issue='reserved'", (session['user'][0],)).fetchall()
        return render_template('my_issues.html', user_name=user_name, role = session['user'][6], user_reservations=user_reservations, user_borrowings=user_borrowings)

@app.route('/cancel_issue', methods=['GET', 'POST'])
def cancel_issue():
    report_id = request.args.get('issue_id')
    # Delete the issue with the given ID from the database
    if report_id:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            report = cursor.execute("SELECT * FROM reports WHERE report_id=?", (report_id,)).fetchone()
        if report[6] == "borrowed":
            book_id = report[2]
            update_query = """
            UPDATE books
            SET copies = copies + 1
            WHERE book_id = ?
        """
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(update_query, (book_id,))
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            issue = "returned"
            cursor.execute("UPDATE reports SET issue = ? WHERE report_id = ?", (issue, report_id,))
    return redirect(url_for('my_issues'))

def new_borrowing(book_id, title, student_id, start_of_week, end_of_week, copies):
    user_name = session['user_name']
    reports_this_week_query = """
        SELECT *
        FROM reports
        WHERE user_id=? AND date>=? AND date<=?
    """
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(reports_this_week_query, (student_id, start_of_week, end_of_week))
    reports_this_week = cursor.fetchall()
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (student_id))
    user = cursor.fetchone()
    role = user[6]
    school_id = user[5]
    num_books_this_week = sum(1 for r in reports_this_week)
    if role == 'student' and num_books_this_week >= 2:
        return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="You have already borrowed 2 books this week!")
    elif role == 'professor' and num_books_this_week >= 1:
        return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="You have already borrowed 1 book this week!")
    if copies == 0:
        issue="onhold"
        message="There are no copies of this book left .. Your are in the waiting list!"
    else:
        issue="borrowed"
        update_query = """
            UPDATE books
            SET copies = copies - 1
            WHERE book_id = ?
        """
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, (book_id,))
        message="The borrowing has been submitted successfully !"
    
    issue_date=date.today() + timedelta(days=14)
    return_date = date.today() + timedelta(days=14)
    new_borrowing_query = """
    INSERT INTO reports (user_id, book_id, title, issue_date, issue, school_id)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(new_borrowing_query, (student_id, book_id, title, issue_date, issue, school_id))
    return message      

@app.route('/book_operations', methods=['GET', 'POST'])
def book_operations():
    if request.method == 'GET':
        user_name = session['user_name']
        isbn = request.args.get('isbn')
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM books WHERE isbn = ?", (isbn,))
        book = cursor.fetchone()  

        session['book_id'] = book[0]
        session['title'] = book[2]
        session['copies'] = book[6]
        if book[0]:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ratings WHERE book_id = ?", (book[0],))
            reviews = cursor.fetchall()        
        return render_template('book_operations.html', user_name=user_name, role = session['user'][6], reviews=reviews)
    else:
        student_id = request.form.get("student_id")
        issue_date = request.form.get("date")
        review_text = request.form.get("review_text")
        rating = request.form.get("rating")
        user_id = session['user'][0]
        school_id = session['user'][5]
        user_name = session['user_name']
        book_id = session['book_id']
        title = session['title']
        copies = session['copies']

         # Cancel any expired reservations
        if issue_date:
            try:
                date = datetime.datetime.strptime(issue_date, '%Y-%m-%d').date()
            except ValueError:                
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Invalid Date. Dates should be in the form Y-M-D, ex. 2023-05-26")  
            today = date.today()
        else:
            today = datetime.date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        expired_reservations_query = """
            DELETE FROM reports
            WHERE book_id=? AND issue_date<=? AND issue='reserved'
        """
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(expired_reservations_query, (book_id, today - timedelta(days=7)))
        
        if student_id:
            message = new_borrowing(book_id, title, student_id, start_of_week, end_of_week, copies)
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message=message)  

        # Check if the user is a student or professor
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchall()  
        role = user[0][6]
        if role == 'student':
                mode=False
        else:
            mode=True
        if not issue_date and not rating and not review_text and not student_id:
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="All fields are empty !")

        if rating or review_text:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ratings (user_id, book_id, title, rating, review_text, mode) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, book_id, title, rating, review_text, mode)
                )
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Your rating was submitted successfully !")

        if issue_date:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM reports WHERE book_id=? AND user_id=? AND issue=? LIMIT 1",
                    (book_id, user_id, "borrowed")
                )
            borrowed = cursor.fetchone()
            if borrowed:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Before you reserve another copy of this book you have to return yours. ")

            #Find late returns to evaluate user
            issue_date = today - datetime.timedelta(days=1)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT *
                FROM reports
                WHERE user_id = ? AND issue_date = ? AND issue = 'borrowed'
                """, (user_id, issue_date))
            search = cursor.fetchall()
            if search:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Before you reserve this book you have to return the book you borrowed. ")

            # Fetch the reports within the current week for the specified user
            reports_this_week_query = """
                SELECT *
                FROM reports
                WHERE user_id=? AND date>=? AND date<=?
            """
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(reports_this_week_query, (user_id, start_of_week, end_of_week))
            reports_this_week = cursor.fetchall()
            
            num_books_this_week = sum(1 for r in reports_this_week)
            # Check if the user has exceeded the borrowing limit for this week
            if role == 'student' and num_books_this_week >= 2:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="You have already reserved 2 books this week!")
            elif role == 'professor' and num_books_this_week >= 1:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="You have already reserved 1 book this week!")
            if copies == 0:
                issue="onhold"
                message="There are no copies of this book left .. Your are in the waiting list!"
            else:
                issue="reserved"
                message="Your reservation request was submitted successfully !"
            
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute( "INSERT INTO reports (user_id, book_id, title, issue_date, issue, school_id) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, book_id, title, issue_date, issue, school_id))

            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message=message)    
        return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Error")    

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
        user_id = random.randrange(10000, 100000)
        user_name = request.form.get("user_name")
        user_password = request.form.get("user_password")
        name = request.form.get("name")
        age = request.form.get("age")
        role = request.form.get("role")
        school_name = request.form.get("school_name")

        if not user_name or not user_password or not name or not age or not role or not school_name:
            return render_template('register.html', error_message="All fields are required !")
        
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            school = cursor.execute("SELECT * FROM schools WHERE school_name=?", (school_name,)).fetchone()
        if not school:
            return render_template('register.html', error_message="This Library Online Management System can support Schools: Athens College, Pierce, Arsakeion, Geitonas School, Kessaris, St. Lawrence College,St. Catherines College, Byron College, Campion School, ACS Athens")
        school_id=school[0]

        # Insert the new user into the users table
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (user_id, user_name, user_password, name, age, school_id, role, approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_name, user_password, name, age, school_id, role, False)
            )
        return redirect(url_for('success'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/users',methods=['GET', 'POST'])
def users():
    user_name = session['user_name']
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if user_id:
            approved = True
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                new_user = cursor.execute("UPDATE users SET approved = ? WHERE user_id = ?", (approved, user_id,)).fetchone()
        approved = False
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            new_users = cursor.execute("SELECT * FROM users WHERE approved= ?", (approved,)).fetchall()
        all = request.args.get('all')
        if all:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                approved = True
                all_users = cursor.execute("SELECT * FROM users WHERE approved = ?",(approved,)).fetchall()
                return render_template('users.html', user_name=user_name, role = session['user'][6], all_users=all_users)  
        name = request.args.get('user_name')
        if name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user = cursor.execute("DELETE FROM users WHERE user_name = ?", (name,)).fetchone()
            return redirect(url_for('users'))        
        return render_template('users.html', user_name=user_name, role = session['user'][6], new_users=new_users)   
    else:
        by_user = request.form.get('by_user')
        if by_user:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user = cursor.execute("SELECT * FROM users WHERE user_id=?", (by_user,)).fetchone()
            return render_template('users.html', user_name=user_name, role = session['user'][6], user=user)  
        return render_template('users.html', user_name=user_name, role = session['user'][6])  

@app.route('/admin1', methods=['GET', 'POST'])
def admin1():
    user_name = session['user_name']
    with open('SQL/views.sql', 'r') as file:
        query = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        results = cursor.executescript(query)
    return render_template('admin1.html', user_name=user_name, role = session['user'][6], results=results)

if __name__ == "__main__":
    app.run()