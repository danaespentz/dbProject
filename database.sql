CREATE TABLE users (
    user_id SERIAL PRIMARY KEY AUTO_INCREMENT,
    user_name VARCHAR NOT NULL,
    user_password VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    school_name VARCHAR NOT NULL,
    role VARCHAR NOT NULL
);

CREATE TABLE schools (
    school_id SERIAL PRIMARY KEY AUTO_INCREMENT,
    school_name VARCHAR NOT NULL,
    postcode VARCHAR NOT NULL,
    town VARCHAR NOT NULL,
    telephone INT NOT NULL,
    email VARCHAR NOT NULL,
    principal_name VARCHAR NOT NULL,
    admin_id VARCHAR NOT NULL
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY AUTO_INCREMENT,
    isbn VARCHAR,
    title VARCHAR,
    author VARCHAR,
    publisher VARCHAR,
    pages INT,
    copies INT,
    theme_categories VARCHAR,
    language_ VARCHAR,
    keywords VARCHAR,
    cover_page VARCHAR
);

CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    date INT NOT NULL,
    issue VARCHAR NOT NULL
    CONSTRAINT fk_review_book FOREIGN KEY (book_id)
  REFERENCES address (books) ON DELETE RESTRICT ON UPDATE CASCADE 
    CONSTRAINT fk_report_user FOREIGN KEY (user_id)
  REFERENCES address (users) ON DELETE RESTRICT ON UPDATE CASCADE 
);

CREATE TABLE ratings (
    rating_id SERIAL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    rating INT NOT NULL,
    review_text VARCHAR
    CONSTRAINT fk_rating_book FOREIGN KEY (book_id)
  REFERENCES address (books) ON DELETE RESTRICT ON UPDATE CASCADE  
    CONSTRAINT fk_rating_user FOREIGN KEY (user_id)
  REFERENCES address (users) ON DELETE RESTRICT ON UPDATE CASCADE 
);