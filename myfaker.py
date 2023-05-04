from faker import Faker
import random

fake = Faker()

# Generate fake data for books
books = []
for _ in range(100):
    title = fake.catch_phrase()
    authors = fake.name()
    isbn = fake.unique.isbn10()
    publisher = fake.company()
    pages = random.randint(100, 500)
    copies = random.randint(1, 10)
    theme_categories = fake.words(nb=3)
    language = fake.language_code()
    keywords = fake.words(nb=5)
    cover_page = fake.url()
    book = {
        'title': title,
        'authors': authors,
        'isbn': isbn,
        'publisher': publisher,
        'pages': pages,
        'copies': copies,
        'theme_categories': theme_categories,
        'language': language,
        'keywords': keywords,
        'cover_page': cover_page
    }
    books.append(book)

for book in books:
    print(book['authors'])