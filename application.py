import sqlite3, re, shutil, os, random
from datetime import date, timedelta
from flask import Flask, session, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from myfaker import books, book_categories, author_names, abstracts

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

@app.route('/backup', methods=['GET','POST'])
def backup():
    if 'user_name' in session and session['user_name'] == 'admin':
        if not os.path.exists('backups'):
            os.makedirs('backups')
        backup_file = 'backups/database_copy.db'
        shutil.copyfile('database.db', backup_file)
        flash('Backup created successfully.', 'success')
    else:
        flash('You are not authorized to perform this operation.', 'danger')
    return redirect(url_for('index'))

@app.route('/restore', methods=['GET','POST'])
def restore():
    if 'user_name' in session and session['user_name'] == 'admin':
        backup_file = 'backups/database_copy.db'
        if os.path.isfile(backup_file):
            shutil.copyfile(backup_file, 'database.db')
            flash('Database restored successfully.', 'success')
        else:
            flash('Backup file does not exist.', 'danger')
    else:
        flash('You are not authorized to perform this operation.', 'danger')
    return redirect(url_for('index'))

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
        user_name = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        if 'user_id' in session:
            user_id = session['user_id']
        else:
            user_id = session['user'][0]
        if user_name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET user_name=? WHERE user_id=?", (user_name, user_id,))
        if name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET name=? WHERE user_id=?", (name, user_id,))
        if password:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET user_password=? WHERE user_id=?", (password, user_id,))
        if name or password or user_name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user = cursor.fetchone()
            flash('Profile updated successfully.', 'success')
            if 'user_id' not in session:
                session.pop('user_name', None)
                session.pop('user', None)
                session['user'] = user
                session['user_name'] = user[1]
                return redirect(url_for('my_profile'))
            else:
                session.pop('user_id', None)
                return redirect(url_for('users'))
        if request.form['submit_button'] == 'Remove':
            user_name=session['user'][1]
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user = cursor.execute("DELETE FROM users WHERE user_name = ?", (user_name,)).fetchone()
            session.pop('user', None)
            session.pop('user_name', None)
            return redirect(url_for('login')) 
    elif request.method == 'GET':
        user_id = request.args.get("user_id")
        editing = request.args.get("editing")
        if user_id:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            user = cursor.fetchone()  
            session['user_id'] = user[0]
            return render_template('myprofile.html', role=session['user'][6], user_name=session['user'][1], user=user, editing=editing)
        return render_template('myprofile.html', role=session['user'][6], user_name=session['user'][1], user = session['user'], editing=editing)
    return render_template('myprofile.html', role=session['user'][6], user_name=session['user'][1], user=session['user'])

def reload_issues(school_id, user_id, role):
    #Refresh "onhold" loans and report users
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE issue=? AND user_id=?", ("onhold",user_id,))
    reports=cursor.fetchall()
    for report in reports:
        if user_id=='11111':
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books WHERE book_id=?", (report[2],))
        else:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books WHERE book_id=? AND school_id=?", (report[2],school_id,))
        book = cursor.fetchone() 
        if book[6]>0:
            flash(f"A copy of the book '{book[2]}' is now available.", 'success')
    #Refresh reservations and remove late pickup after one week
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE issue=? AND user_id=?", ("reserved",user_id,))
    reports=cursor.fetchall()
    for report in reports:        
        reserved_date = datetime.datetime.strptime(report[5], "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (today - reserved_date).days
        if days>=7:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM reports WHERE report_id = ?", (report[0],)).fetchone()
            flash(f"Your reservation for the book '{report[3]}' was canceled. You were late {days} days :(", 'success')
    #Refresh issus to find bad users
    today = datetime.date.today()
    if role == "School Admin" or role == "Admin":
        bad_users = []
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE school_id = ?", (school_id,))
        users = cursor.fetchall() 
        for user in users:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE user_id = ? AND issue = 'borrowed'", (user[0],))
            search = cursor.fetchall()    
            if search:
                for result in search:
                    issue_date = datetime.datetime.strptime(result[5], '%Y-%m-%d').date()
                    days = (today - issue_date).days
                    if days > 0:
                        bad_users.append(user[0])
        session['bad_users'] = bad_users
    else:
        bad_users = []
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            user = cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE user_id = ? AND issue = 'borrowed'", (user_id,))
        search = cursor.fetchall()    
        if search:
            for result in search:
                issue_date = datetime.datetime.strptime(result[5], '%Y-%m-%d').date()
                days = (today - issue_date).days
                if days > 0:
                    bad_users.append(user_id)
                    break
        session['bad_users'] = bad_users

@app.route('/new_books', methods=['GET', 'POST'])
def new_book():
    if request.method == 'GET':
        user_name = session['user_name']
        return render_template('new_book.html', user_name=user_name, role=session['user'][6])
    else:
        user_name = session['user_name']
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        authors = request.form.get("authors")
        publisher = request.form.get("publisher")
        pages = request.form.get("pages")
        copies = request.form.get("copies")
        theme_categories = request.form.get("theme_categories")
        language = request.form.get("language")
        keywords = request.form.get("keywords")
        cover_page = request.files['cover_page']
        abstract = request.form.get("abstract")
        school_id = request.form.get("school_id")

        if not title or not isbn or not authors or not publisher or not pages or not copies or not theme_categories or not language or not keywords or not cover_page or not school_id:
            return render_template('new_book.html', error_message=cover_page)

        filename = secure_filename(cover_page.filename)
        file_path = os.path.join('static/book_covers/', filename)
        cover_page.save(file_path)

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (isbn, title, authors, publisher, pages, copies, theme_categories, language, keywords, cover_page, abstract, school_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (isbn, title, authors, publisher, pages, copies, theme_categories, language, keywords, file_path, abstract, school_id)
            )
        flash("Your book was added successfully!", 'success')
        return render_template('new_book.html', user_name=user_name, role=session['user'][6])

@app.route('/new_school', methods=['GET', 'POST'])
def new_school():
    if request.method == 'GET':
        user_name = session['user_name']
        return render_template('new_school.html', user_name=user_name, role=session['user'][6])
    else:
        user_name = session['user_name']
        school_id = random.randrange(10000, 99999)
        school_name = request.form.get("school_name")
        postcode = request.form.get("postcode")
        town = request.form.get("town")
        telephone = request.form.get("telephone")
        email = request.form.get("email")
        principal_name = request.form.get("principal_name")
        operator_name = request.form.get("operator_name")
        admin_id = random.randrange(10000, 99999)

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO schools (school_id, school_name, postcode, town, telephone, email, principal_name, operator_name, admin_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (school_id, school_name, postcode, town, telephone, email, principal_name, operator_name, admin_id)
            )
        return render_template('new_school.html', user_name=user_name, role=session['user'][6])

@app.route('/<user_name>/home', methods=['GET', 'POST'])
def home(user_name):
    if request.method == 'GET':
        if 'user_name' in session:
            reload_issues(session['user'][5], session['user'][0], session['user'][6])
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
            if session['user'][0] == 11111:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE title=?", (title,))
            else:    
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE title=? AND school_id=?", (title,session['user'][5],))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message = "There is no book with this title!")
        if authors:
            if session['user'][0] == 11111:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE authors LIKE ?", (f'%{authors}%',))
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE authors LIKE ? AND school_id=?", (f'%{authors}%',session['user'][5],))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message = "There are no books by this author!")
        if theme_categories:
            if session['user'][0] == 11111:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE theme_categories LIKE ?", (f'%{theme_categories}%',))
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE theme_categories LIKE ? AND school_id=?", (f'%{theme_categories}%',session['user'][5],))
            results = cursor.fetchall()
            if not results:
                return render_template('home.html', user_name=user_name, role = session['user'][6], error_message="Book Categories are: Fiction, Non-Fiction, Mystery, Thriller, Biography, History, Science Fiction, Romance, Cooking, Poetry. It is important to spell them correctly!")
        if copies:
            if session['user'][0] == 11111:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE copies=?", (copies,))
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE copies=? AND school_id=?", (copies,session['user'][5],))
            results = cursor.fetchall()
        if not results:
            return render_template('search_results.html', user_name=user_name, role = session['user'][6], error_message="Not found.. Sorry")
        else:
            return render_template('search_results.html', user_name=user_name, role = session['user'][6], results=results)

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    user_name = session['user_name']
    return render_template('search_results.html', user_name=user_name, role = session['user'][6])

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
        search = []
        borrow_results = []
        if name:
            if user_name == "admin":
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE name=?",(name,))
                user = cursor.fetchone()
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE name=? AND school_id = ?",(name, str(session['user'][5]),))
                user = cursor.fetchone()
            if not user:
                flash('This student is not registrated to your school as Operator', 'danger')
                return redirect(url_for('lateBorrowings'))
            user_id = user[0]
        if latedays:    
            try:
                days = int(latedays)
            except ValueError:
                return render_template('lateBorrowings.html', user_name=user_name, role = session['user'][6], error_message="Invalid number of days!")
        if name and latedays:    
            issue_date = today - datetime.timedelta(days=days)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE user_id = ? AND issue_date = ? AND issue = 'borrowed'", (user_id, issue_date))
            borrow_results = cursor.fetchall()      
        elif name:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE user_id = ? AND issue = 'borrowed'", (user_id,))
            search = cursor.fetchall()    
            if search:
                for result in search:
                    issue_date = datetime.datetime.strptime(result[5], '%Y-%m-%d').date()
                    days = (today - issue_date).days
                    if days > 0:
                        borrow_results.append([result,days])
                return render_template('search_borrowings.html', user_name=user_name, role = session['user'][6], results=borrow_results) 
        elif latedays:
            issue_date = today - datetime.timedelta(days=days)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE issue_date = ? AND issue = 'borrowed'", (issue_date,))
            borrow_results = cursor.fetchall()  
        if borrow_results:   
            return render_template('search_borrowings.html', user_name=user_name, role = session['user'][6], results=borrow_results, days=days)
        else:
            flash("No results.. :(", 'info')
        return redirect(url_for('lateBorrowings'))

@app.route('/search_borrowings')
def search_borrowings():
    return redirect(url_for('search_borrowings'))

@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
    if request.method == 'GET':
        user_name = session['user_name']
        return render_template('ratings.html', user_name=user_name, role = session['user'][6])
    else:
        user_name = session['user_name']
        by_user = request.form.get("by_user")
        by_category = request.form.get("by_category")

        if not by_user and not by_category:
            return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="All fields are empty !")
    
        results = []
        if by_user:
            if user_name == "admin":
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE name=?",(by_user,))
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE name=? AND school_id = ?",(by_user, str(session['user'][5]),))
            user = cursor.fetchone()
            if not user:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="There is no student with this name at this school")
            user_id = user[0]
        if by_category and by_user:
            MO = 0
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM books WHERE theme_categories LIKE ? AND school_id=?", (f'%{by_category}%',user[5],))
            search = cursor.fetchall()    
            if search:
                count = 0 
                for book in search:
                    book_id = book[0]
                    with sqlite3.connect('database.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM ratings WHERE book_id = ? AND user_id = ?", (book_id, user_id))
                    ratings = cursor.fetchall()
                    if ratings:
                        for result in ratings:
                            count = count + 1
                            MO = MO + result[4]
                if count:
                    MO = round(MO / count, 2)
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], category = by_category, name = by_user, MO=MO)
            else:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="Incorrect Book category")
        if by_user:
            MO = 0
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ratings WHERE user_id = ?", (user_id,))
            search = cursor.fetchall()
            if search:
                count = 0 
                for result in search:
                    count = count + 1
                    MO = MO + int(result[4])
                if count:
                    MO = round(MO / count, 2)
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], name = by_user, MO=MO)
        if by_category:
            count = 0
            MO = 0
            if session['user'][0] == 11111:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE theme_categories LIKE ?", (f'%{by_category}%',))
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM books WHERE theme_categories LIKE ? AND school_id=?", (f'%{by_category}%',session['user'][5],))
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
                    MO = round(MO / count, 2) 
                session['MO'] = MO
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], category = by_category, MO=MO)
            else:
                return render_template('ratings.html', user_name=user_name, role = session['user'][6], error_message="Incorrect Book category")
        return render_template('ratings.html', user_name=user_name, role = session['user'][6])

@app.route('/my_issues',methods=['GET', 'POST'])
def my_issues():
    user_name = session['user_name']
    loans = request.args.get('loans')
    reservations = request.args.get('reservations')
    approvals = request.args.get('approvals')

    if loans:
        if session['user'][6] == "Admin":
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_borrowings = cursor.execute("SELECT * FROM reports WHERE issue='borrowed'").fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], loans=loans, user_borrowings=user_borrowings)   
        if session['user'][6] == "School Admin":
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_borrowings = cursor.execute("SELECT * FROM reports WHERE issue='borrowed' AND school_id = ?",(str(session['user'][5]),)).fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], loans=loans, user_borrowings=user_borrowings)   
        else:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_borrowings = cursor.execute("SELECT * FROM reports WHERE user_id=? AND issue='borrowed'", (session['user'][0],)).fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], loans=loans, user_borrowings=user_borrowings)   
    if reservations:
        if session['user'][6] == "Admin":
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_reservations = cursor.execute("SELECT * FROM reports WHERE issue='reserved'").fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], reservations=reservations, user_reservations=user_reservations)   
        if session['user'][6] == "School Admin":
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_reservations = cursor.execute("SELECT * FROM reports WHERE issue='reserved' AND school_id = ?",(str(session['user'][5]),)).fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], reservations=reservations, user_reservations=user_reservations)   
        else:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                user_reservations = cursor.execute("SELECT * FROM reports WHERE user_id=? AND issue='reserved'", (session['user'][0],)).fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], reservations=reservations, user_reservations=user_reservations)   
    if session['user'][6] == "Admin":
        rating_id = request.args.get('rating_id')
        if rating_id:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE ratings SET mode=1 WHERE rating_id=?", (rating_id,))
        if approvals:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                rating_approvals = cursor.execute("SELECT * FROM ratings R INNER JOIN users U ON R.user_id = U.user_id WHERE R.mode=0").fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], approvals=approvals, rating_approvals=rating_approvals)   
    if session['user'][6] == "School Admin":
        rating_id = request.args.get('rating_id')
        if rating_id:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE ratings SET mode=1 WHERE rating_id=?", (rating_id,))
        if approvals:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                rating_approvals = cursor.execute("SELECT * FROM ratings R INNER JOIN users U ON R.user_id = U.user_id WHERE U.school_id = ? AND R.mode=0",(str(session['user'][5]),)).fetchall()
            return render_template('my_issues.html', user_name=user_name, role = session['user'][6], approvals=approvals, rating_approvals=rating_approvals)   
    return render_template('my_issues.html', user_name=user_name, role = session['user'][6])   

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
            update_query = "UPDATE books SET copies = copies + 1 WHERE book_id = ?"
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(update_query, (book_id,))
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reports SET issue = ? WHERE report_id = ?", ("returned", report_id,))
    return redirect(url_for('my_issues'))

@app.route('/borrowed_issue', methods=['GET', 'POST'])
def borrowed_issue():
    report_id = request.args.get('issue_id')
    # Delete the issue with the given ID from the database
    if report_id:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            book_id = cursor.execute("SELECT book_id FROM reports WHERE report_id=?", (report_id,)).fetchone()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reports SET issue = ? WHERE report_id = ?", ("borrowed", report_id,))
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE books SET copies = copies - 1 WHERE book_id =?", (book_id[0],))
    return redirect(url_for('my_issues'))

def new_borrowing(book_id, title, student_id, start_of_week, end_of_week, copies):
    user_name = session['user_name']
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reports WHERE user_id = ? AND book_id = ? AND issue = 'borrowed'", (student_id, book_id,))
    search = cursor.fetchall()
    if search:
        message="Before you borrow another copy of this book you have to return yours"
        return message
    
    loans_this_week_query = "SELECT * FROM reports WHERE user_id=? AND issue=? AND date>=? AND date<=?"
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute(loans_this_week_query, (student_id, "borrowed", start_of_week, end_of_week,))
    loans_this_week = cursor.fetchall()
    
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (student_id,))
    user = cursor.fetchone()
    role = user[6]
    school_id = user[5]
    
    num_books_this_week = sum(1 for r in loans_this_week)
    if role == 'student' and num_books_this_week >= 2:
        flash(f"{user[3]} has already borrowed 2 books this week", 'success')        
        return
    elif role == 'professor' and num_books_this_week >= 1:
        flash(f"{user[3]} has already borrowed 1 book this week", 'success')        
        return
    if copies == 0:
        issue="onhold"
        message="There are no copies of this book left .. Your are in the waiting list!"
    else:
        issue="borrowed"
        update_query = "UPDATE books SET copies = copies - 1 WHERE book_id = ? AND school_id=?"
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(update_query, (book_id,school_id,))
        message="The borrowing has been submitted successfully !"
    
    issue_date=date.today() + timedelta(days=14)
    return_date = date.today() + timedelta(days=14)
    new_borrowing_query = "INSERT INTO reports (user_id, book_id, title, issue_date, issue, school_id) VALUES (?, ?, ?, ?, ?, ?)"
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
            cursor.execute("SELECT * FROM books WHERE isbn = ? AND school_id=?", (isbn, session['user'][5]))
        book = cursor.fetchone()  
        session['book_id'] = book[0]
        session['title'] = book[2]
        session['copies'] = book[6]
        if book[0]:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM ratings WHERE book_id = ? AND mode=1", (book[0],))
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

        if issue_date:
            try:
                date = datetime.datetime.strptime(issue_date, '%Y-%m-%d').date()
            except ValueError:                
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Invalid Date. Dates should be in the form Y-M-D, ex. 2023-05-26")  
            today = date.today()
            if date < today:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Invalid Date.")  
            bad_users = session['bad_users']
            if int(user_id) in bad_users:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Reservation Criteria Not Met: we kindly remind you that there are overdue books that need to be returned promptly.")  
        else:
            today = datetime.date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        if student_id:
            bad_users = session['bad_users']
            if int(student_id) in bad_users:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="This student doesn't meet the loan criteria")  
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (student_id,))
            user = cursor.fetchall() 
            school_id = session['user'][5]
            if user[0][5] == school_id:
                message = new_borrowing(book_id, title, student_id, start_of_week, end_of_week, copies)
            else:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="You are authorized to loan books only to your school's students!")  
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message=message)  

        # Check if the user is a student or professor
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchall()  
        role = user[0][6]
        if not issue_date and not rating and not review_text:
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="All fields are empty !")

        if rating or review_text:
            if role == 'student' and review_text:
                mode='0'
            else:
                mode='1'
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO ratings (user_id, book_id, title, rating, review_text, mode) VALUES (?, ?, ?, ?, ?, ?)",(user_id, book_id, title, rating, review_text, mode,))
            return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Your rating was submitted successfully !")

        if issue_date:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE book_id=? AND user_id=? AND issue=? LIMIT 1",(book_id, user_id, "borrowed",))
            borrowed = cursor.fetchone()
            if borrowed:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Before you reserve another copy of this book you have to return yours. ")

            #Find late returns to evaluate user
            issue_date = today - datetime.timedelta(days=1)
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM reports WHERE user_id = ? AND issue_date = ? AND issue = 'borrowed'", (user_id, issue_date))
            search = cursor.fetchall()
            if search:
                return render_template('book_operations.html', user_name=user_name, role = session['user'][6], message="Before you reserve this book you have to return the book you borrowed. ")

            # Fetch the reports within the current week for the specified user
            reservations_this_week_query = "SELECT * FROM reports WHERE user_id=? AND issue=? AND date>=? AND date<=?"
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute(reservations_this_week_query, (user_id, "reserved", start_of_week, end_of_week))
            reservations_this_week = cursor.fetchall()
            
            num_books_this_week = sum(1 for r in reservations_this_week)
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
    session.pop('user', None)
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
            return render_template('register.html', error_message="This Library Online Management System can support Schools: Athens College, Pierce, Arsakeion, Geitonas School, St. Catherines College, ACS Athens")
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
    if user_name == "admin":
        selectAll=True
    else:
        selectAll = False
    if request.method == 'GET':
        user_id = request.args.get('user_id')
        if user_id:
            approved = True
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                new_user = cursor.execute("UPDATE users SET approved = ? WHERE user_id = ?", (approved, user_id,)).fetchone()
        approved = False
        if selectAll:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                new_users = cursor.execute("SELECT * FROM users WHERE approved= ?",(approved,)).fetchall()
        else:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                new_users = cursor.execute("SELECT * FROM users WHERE approved= ? AND school_id = ?",(approved, str(session['user'][5]),)).fetchall()
        all = request.args.get('all')
        if all:
            if selectAll:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    approved = True
                    all_users = cursor.execute("SELECT * FROM users WHERE approved = ?",(approved,)).fetchall()
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    approved = True
                    all_users = cursor.execute("SELECT * FROM users WHERE approved = ? AND school_id = ?",(approved, str(session['user'][5]),)).fetchall()
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
            if selectAll:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    user = cursor.execute("SELECT * FROM users WHERE user_id=?",(by_user,)).fetchone()
            else:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    user = cursor.execute("SELECT * FROM users WHERE user_id=? AND school_id = ?",(by_user, str(session['user'][5]),)).fetchone()
            return render_template('users.html', user_name=user_name, role = session['user'][6], user=user)  
        return render_template('users.html', user_name=user_name, role = session['user'][6])  

@app.route('/admin_views', methods=['GET', 'POST'])
def admin_views():
    user_name = session['user_name']
    return render_template('admin_views.html', user_name=user_name, role = session['user'][6])

@app.route('/view1', methods=['GET', 'POST'])
def view1():
    year = request.form.get('year')
    monthYear = request.form.get('monthYear')
    user_name = session['user_name']
    if monthYear:
        if not re.match(r'^\d{4}-\d{2}$', monthYear):
            flash("Dates can be in the format of year (ex.2023, 2022) or monthYear (ex. 2023-05, 2023-08)", 'success')
        else:
            with open('SQL/views.sql', 'r') as file:
                query1 = file.read()
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.executescript(query1)
                view1 = cursor.execute("SELECT * FROM borrowings_per_school_per_monthYear WHERE date = ?", (monthYear,))
                results = view1.fetchall()
            return render_template('view1.html', user_name=user_name, role=session['user'][6], view1=results)
    if year:
        with open('SQL/views.sql', 'r') as file:
            query1 = file.read()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.executescript(query1)
            view1 = cursor.execute("SELECT * FROM borrowings_per_school_per_year WHERE date = ?", (year,))
            results = view1.fetchall()
        return render_template('view1.html', user_name=user_name, role=session['user'][6], view1=results)
    return render_template('view1.html', user_name=user_name, role=session['user'][6])

@app.route('/view2', methods=['GET', 'POST'])
def view2():
    user_name = session['user_name']
    category = request.form.get('category')
    if category not in book_categories:
        flash("Book Categories are: Fiction, Non-Fiction, Mystery, Thriller, Biography, History, Science Fiction, Romance, Cooking, Poetry. It is important to spell them correctly!", 'danger')
    elif category:
        with open('SQL/views2.sql', 'r') as file:
            query2 = file.read()
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.executescript(query2)
            view1 = cursor.execute("SELECT name FROM borrowings_per_category WHERE category = ?", (category,))
            results1 = view1.fetchall()
            view2 = cursor.execute("SELECT authors FROM bookids_AND_authors_per_category WHERE theme_category = ?", (category,))
            results2 = view2.fetchall()
        
        name_list1 = [name[0] for name in results1]
        name_list2 = [name.strip() for name in results2[0][0].split(',') if name.strip()]
        return render_template('view2.html', user_name=user_name, role=session['user'][6], category=category, view1=name_list1, view2=name_list2)
    return render_template('view2.html', user_name=user_name, role=session['user'][6])

@app.route('/view3', methods=['GET', 'POST'])
def view3():
    user_name = session['user_name']
    with open('SQL/views3.sql', 'r') as file:
        query3 = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(query3)
        view1 = cursor.execute("SELECT * FROM borrowings_per_young_professors")
        results = view1.fetchall()
    return render_template('view3.html', user_name=user_name, role=session['user'][6], view3=results)

@app.route('/view4', methods=['GET', 'POST'])
def view4():
    user_name = session['user_name']
    with open('SQL/views4.sql', 'r') as file:
        query4 = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(query4)
        view4 = cursor.execute("SELECT * FROM authors_with_borrowed_books")
        results = view4.fetchall()
        authors=list()
        for result in results:
            authors.append(result[0])
        bad_authors = set(author_names) - set(authors)
    if not bad_authors:
        return render_template('view4.html', user_name=user_name, role=session['user'][6], view4=authors, error_message="Sorry, all authors have borrowed books.. The list above is the authors list!")
    return render_template('view4.html', user_name=user_name, role=session['user'][6], view4=bad_authors)

@app.route('/view5', methods=['GET', 'POST'])
def view5():
    user_name = session['user_name']
    with open('SQL/views5.sql', 'r') as file:
        query5 = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(query5)
        view5 = cursor.execute("SELECT * FROM same_loans_per_admin")
        results = view5.fetchall()
    if not results:
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            view5 = cursor.execute("SELECT * FROM loans_per_admin")
        return render_template('view5.html', user_name=user_name, role=session['user'][6], view5=view5, error_message="Sorry, there are no such operators..")
    return render_template('view5.html', user_name=user_name, role=session['user'][6], view5=results)

@app.route('/view6', methods=['GET', 'POST'])
def view6():
    user_name = session['user_name']
    with open('SQL/views6.sql', 'r') as file:
        query6 = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(query6)
        view6 = cursor.execute("SELECT category1, category2, common_book_count FROM common_book_ids_per_category_pair LIMIT 3;")
        results = view6.fetchall()
    if not results:
        return render_template('view6.html', user_name=user_name, role=session['user'][6], error_message="Sorry, something went wrong..")
    return render_template('view6.html', user_name=user_name, role=session['user'][6], view6=results)

@app.route('/view7', methods=['GET', 'POST'])
def view7():
    user_name = session['user_name']
    with open('SQL/views7.sql', 'r') as file:
        query7 = file.read()
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.executescript(query7)
        view7 = cursor.execute("SELECT * FROM books_per_author")
        results = view7.fetchall()
    if not results:
        return render_template('view7.html', user_name=user_name, role=session['user'][6], error_message="Sorry, something went wrong..")
    return render_template('view7.html', user_name=user_name, role=session['user'][6], view7=results)

if __name__ == "__main__":
    app.run()