-- Create the 'users' table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    user_password TEXT NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    school_name TEXT NOT NULL,
    role TEXT NOT NULL,
    approved INTEGER DEFAULT 0
);

-- Create the 'schools' table
CREATE TABLE IF NOT EXISTS schools (
    school_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_name TEXT NOT NULL,
    postcode TEXT NOT NULL,
    town TEXT NOT NULL,
    telephone INTEGER NOT NULL,
    email TEXT NOT NULL,
    principal_name TEXT NOT NULL,
    admin_id TEXT NOT NULL
);

-- Create the 'books' table
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT,
    title TEXT,
    authors TEXT,
    publisher TEXT,
    pages INTEGER,
    copies INTEGER,
    theme_categories TEXT,
    language TEXT,
    keywords TEXT,
    cover_page TEXT
);

-- Create the 'reports' table
CREATE TABLE IF NOT EXISTS reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    issue_date DATE NOT NULL,
    issue TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Create the 'ratings' table
CREATE TABLE IF NOT EXISTS ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    rating INTEGER,
    review_text TEXT,
    mode INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books (book_id) ON DELETE RESTRICT ON UPDATE CASCADE
);