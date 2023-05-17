import sqlite3
from myfaker import books

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

with open('create_tables.sql', 'r') as file:
    create_tables_query = file.read()
    cursor.executescript(create_tables_query)
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