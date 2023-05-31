import sqlite3, random
from myfaker import books, book_categories, author_names
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

with open('SQL/create_indexes.sql', 'r') as file:
    indexes_query = file.read()
    cursor.executescript(indexes_query)
    connection.commit()

# Insert the generated books into the database
school_ids = ['12345', '23456', '34567', '45678', '67890', '01234']
for school_id in school_ids:
    for book in books:
        cursor.execute(
            "INSERT INTO books (title, authors, isbn, publisher, pages, copies, theme_categories, language, keywords, cover_page, abstract, school_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                book['abstract'],
                school_id,
            )
        )
connection.commit()
for category in book_categories:
    cursor.execute(""" SELECT * FROM books WHERE theme_categories LIKE ? """, (f'%{category}%',))
    search = cursor.fetchall()
    authors = ''
    book_ids = ''
    for book in search:
        authors+=book[3] + ','
        book_ids+=str(book[0]) + ', '
        A = book[3].split(',')
        for author in A:
            author=author.strip()
    cursor.execute( "INSERT INTO bookids_AND_authors_per_category (theme_category, authors, book_ids) VALUES (?, ?, ?)", (str(category), authors, book_ids,))
for author in author_names:
    cursor.execute( "INSERT INTO authors (author) VALUES (?)", (author,))
connection.commit()
cursor.execute(""" SELECT user_id, school_id, role FROM users """)
users = cursor.fetchall()
cursor.execute(""" SELECT book_id, title FROM books """)
library = cursor.fetchall()
selected_books = random.sample(library, 80)
issue_types = ['returned', 'reserved', 'borrowed']
ratings = ['Excellent', 'Engaging', 'Captivating', 'Fascinating', 'Inspiring', 'Thought-provoking', 'Thrilling', 'Mediocre', 'Disappointing', 'Dull']
i=0

for user in users:
    # Generate a random number of reports for each user
    if user[2] == "Admin" or user[2]=="School Admin":
        continue
    num_reports = random.randint(0, 10)  # Adjust the range as needed
    for _ in range(num_reports):
        book = random.choice(selected_books)
        report_id = i
        i=i+1
        issue = random.choice(issue_types)
        if issue=="borrowed":
            start_date = datetime.strptime("2023-04-01", "%Y-%m-%d")  # Adjust the start date as needed
            end_date = datetime.strptime("2023-06-03", "%Y-%m-%d")  # Adjust the end date as needed
            date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        else:
            start_date = datetime.strptime("2021-01-01", "%Y-%m-%d")  # Adjust the start date as needed
            end_date = datetime.strptime("2023-06-03", "%Y-%m-%d")  # Adjust the end date as needed
            date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
        if issue == "returned" or issue == "borrowed":
            issue_date = (date + timedelta(weeks=2)).strftime("%Y-%m-%d")
        elif issue == "reserved":
            days_to_add = random.randint(1, 30)
            issue_date = (date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
        
        cursor.execute("INSERT INTO reports (report_id, user_id, book_id, title, date, issue_date, issue, school_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (report_id, user[0], book[0], book[1], date.strftime("%Y-%m-%d"), issue_date, issue, user[1]))
        connection.commit()
    
    num_reviews = random.randint(8, 20)
    for _ in range(num_reviews):
        rating_id = i
        i=i+1
        book = random.choice(library)
        review = random.choice(ratings)
        cursor.execute("INSERT INTO ratings (rating_id, user_id, book_id, title, rating, review_text, mode) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (rating_id, user[0], book[0], book[1], random.randint(1, 5), review, 1))
        connection.commit()