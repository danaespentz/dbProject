from faker import Faker
import random

fake = Faker()

# Generate fake data for books
books = []
book_categories = ["Fiction", "Non-Fiction", "Mystery", "Thriller", "Biography", "History", "Science Fiction", "Romance", "Cooking", "Poetry"]
book_languages = ["English", "Spanish", "French", "German", "Mandarin", "Japanese", "Arabic", "Russian", "Portuguese", "Italian"]

for _ in range(100):
    title = fake.catch_phrase()
    authors = [fake.name() for _ in range(random.randint(1, 3))]
    isbn = fake.unique.isbn10()
    publisher = fake.company()
    pages = random.randint(100, 500)
    copies = random.randint(1, 10)
    theme_categories = random.sample(book_categories, k=random.randint(1,3))
    language = random.choice(book_languages)
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
