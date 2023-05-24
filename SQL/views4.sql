CREATE VIEW authors_with_borrowed_books AS
SELECT DISTINCT A.author
FROM authors A
INNER JOIN books B ON instr(B.authors, A.author) > 0
INNER JOIN reports R ON R.book_id = B.book_id
WHERE (R.issue = 'borrowed' OR R.issue = 'returned');

CREATE VIEW authors_with_no_borrowed_books AS
SELECT DISTINCT A.author
FROM authors A
LEFT JOIN authors_with_borrowed_books AN ON A.author = AN.author
WHERE AN.author IS NULL;
