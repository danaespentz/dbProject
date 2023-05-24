import sqlite3, random
from myfaker import books, book_categories
from datetime import datetime, timedelta

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Read and execute the create tables query
with open('SQL/create_tables.sql', 'r') as file:
    create_tables_query = file.read()
    cursor.executescript(create_tables_query)
    connection.commit()

# Read and execute the insert data query
with open('SQL/insert_data.sql', 'r') as file:
    insert_data_query = file.read()
    cursor.executescript(insert_data_query)
    connection.commit()

# Insert the generated books into the database
for book in books:
    cursor.execute(
        "INSERT INTO books (title, authors, isbn, publisher, pages, copies, theme_categories, language, keywords, cover_page) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            book['title'],
            ', '.join(book['authors']),
            book['isbn'],
            book['publisher'],
            book['pages'],
            book['copies'],
            ', '.join(book['theme_categories']),
            book['language'],
            ', '.join(book['keywords']),
            book['cover_page'],
        )
    )
connection.commit()
AUTHORS = set()
for category in book_categories:
    cursor.execute(""" SELECT * FROM books WHERE theme_categories LIKE ? """, (f'%{category}%',))
    search = cursor.fetchall()
    authors = ''
    book_ids = ''
    for book in search:
        authors+=book[3]
        book_ids+=str(book[0]) + ', '
        A = book[3].split(',')
        for author in A:
            author=author.strip()
            AUTHORS.add(author)
    cursor.execute( "INSERT INTO bookids_AND_authors_per_category (theme_category, authors, book_ids) VALUES (?, ?, ?)", (str(category), authors, book_ids,))
for author in AUTHORS:
    cursor.execute( "INSERT INTO authors (author) VALUES (?)", (author,))
connection.commit()



cursor.execute(""" SELECT user_id, school_id FROM users """)
users = cursor.fetchall()
cursor.execute(""" SELECT book_id, title FROM books """)
books = cursor.fetchall()
issue_types = ['returned', 'reserved', 'borrowed']
ratings = ['Excellent', 'Engaging', 'Captivating', 'Fascinating', 'Inspiring', 'Thought-provoking', 'Thrilling', 'Mediocre', 'Disappointing', 'Dull']
i=0
for user in users:
    # Generate a random number of reports for each user
    num_reports = random.randint(1, 10)  # Adjust the range as needed
    for _ in range(num_reports):
        book = random.choice(books)
        report_id = i
        issue = random.choice(issue_types)
        start_date = datetime.strptime("2021-01-01", "%Y-%m-%d")  # Adjust the start date as needed
        end_date = datetime.strptime("2023-12-31", "%Y-%m-%d")  # Adjust the end date as needed
        date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        if issue == "returned" or issue == "borrowed":
            issue_date = (date + timedelta(weeks=2)).strftime("%Y-%m-%d")
        elif issue == "reserved":
            days_to_add = random.randint(1, 30)
            issue_date = (date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
        
        cursor.execute("INSERT INTO reports (report_id, user_id, book_id, title, date, issue_date, issue, school_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (report_id, user[0], book[0], book[1], date.strftime("%Y-%m-%d"), issue_date, issue, user[1]))
        connection.commit()
        
        review = random.choice(ratings)
        cursor.execute("INSERT INTO ratings (rating_id, user_id, book_id, title, rating, review_text, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (report_id, user[0], book[0], book[1], random.randint(1, 5), review, 1))
        connection.commit()
        i=i+1