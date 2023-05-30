from faker import Faker
import random, os

fake = Faker()

# Generate fake data for books
books = []
cover_files = os.listdir('static/book_covers/')
covers = [file for file in cover_files if file.endswith(('.jpg', '.jpeg', '.png'))]
book_categories = ["Fiction", "Non-Fiction", "Mystery", "Thriller", "Biography", "History", "Science Fiction", "Romance", "Cooking", "Poetry"]
book_languages = ["English", "Spanish", "French", "German", "Mandarin", "Japanese", "Arabic", "Russian", "Portuguese", "Italian"]
author_names = ['Harper Lee', 'J.K. Rowling', 'Ernest Hemingway', 'George Orwell', 'Jane Austen', 'F. Scott Fitzgerald', 'Stephen King', 'Toni Morrison', 'Mark Twain', 'Gabriel Garcia Marquez', 'Virginia Woolf', 'Charles Dickens', 'Leo Tolstoy', 'Hermann Hesse', 'Emily Bronte', 'Ralph Ellison', 'Kazuo Ishiguro', 'Agatha Christie', 'Oscar Wilde', 'John Steinbeck', 'William Faulkner', 'Maya Angelou', 'Terry Pratchett', 'Isabel Allende', 'Chinua Achebe', 'George R.R. Martin', 'Salman Rushdie', 'Zadie Smith', 'Neil Gaiman', 'J.R.R. Tolkien', 'Philip Roth', 'H.P. Lovecraft', 'Mikhail Bulgakov', 'Albert Camus', 'Yukio Mishima', 'Hermann Melville', 'Kurt Vonnegut', 'John Updike', 'Fyodor Dostoevsky', 'Margaret Atwood', 'Ursula K. Le Guin', 'Roald Dahl']
abstracts = [
    "Set in the Jazz Age, the story follows Jay Gatsby, a mysterious millionaire, and his pursuit of the American Dream. F. Scott Fitzgerald explores themes of wealth, love, and disillusionment in this iconic novel.",
    "Harper Lees classic novel portrays the racial tensions of the Deep South through the eyes of Scout Finch. With her father, Atticus, defending a black man accused of rape, Scout learns important lessons about justice, compassion, and empathy.",
    "George Orwells dystopian masterpiece depicts a totalitarian regime where Big Brother watches every move. Winston Smith rebels against the oppressive state, but finds himself trapped in a world where individuality and free thought are dangerous acts.",
    "Jane Austens beloved novel explores the social mores of 19th-century England. Elizabeth Bennet navigates societal expectations, love, and personal growth while challenging the prejudices of her time in this witty and romantic tale.",
    "J.D. Salingers coming-of-age novel follows Holden Caulfield as he rebels against conformity and struggles with his own identity. Through Holdens unique voice, the book explores themes of alienation, adolescence, and the loss of innocence.",
    "J.R.R. Tolkiens fantasy adventure takes readers on a quest with Bilbo Baggins, a hobbit who joins a group of dwarves to reclaim their homeland from the dragon Smaug. Along the way, Bilbo discovers courage, friendship, and the lure of adventure.",
    "This epic trilogy by J.R.R. Tolkien follows the journey of Frodo Baggins as he carries the One Ring to Mount Doom to save Middle-earth. Filled with rich world-building, heroic quests, and battles of good against evil, it has become a staple of fantasy literature.",
    "Herman Melvilles novel is an epic tale of Captain Ahabs obsession with hunting down the white whale, Moby Dick. Through vivid descriptions and philosophical musings, Melville explores themes of fate, vengeance, and the human struggle against nature.",
    "In this modern classic, Gabriel Garcia Marquez tells the story of the Buendia family across generations in the fictional town of Macondo. Magical realism blends with themes of love, solitude, and the cyclical nature of life in this captivating masterpiece.",
    "Aldous Huxleys dystopian novel envisions a future where technology, consumerism, and social conditioning control every aspect of human life. Through the eyes of characters like Bernard Marx and John the Savage, Huxley critiques a society devoid of individuality and genuine emotion."
]
for _ in range(100):
    title = fake.catch_phrase()
    authors = random.sample(author_names, k=random.randint(1,3))
    isbn = fake.unique.isbn10()
    publisher = fake.company()
    pages = random.randint(100, 500)
    copies = random.randint(1, 10)
    theme_categories = random.sample(book_categories, k=random.randint(1,3))
    language = random.choice(book_languages)
    keywords = fake.words(nb=5)
    cover_page = 'static/book_covers/' + random.choice(covers)
    abstract = random.choice(abstracts)
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
        'cover_page': cover_page,
        'abstract': abstract
    }
    books.append(book)
