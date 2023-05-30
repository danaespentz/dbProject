CREATE VIEW IF NOT EXISTS books_per_author AS
SELECT A.author, COUNT(B.book_id) AS count
FROM authors A
INNER JOIN books B ON instr(B.authors, A.author) > 0
GROUP BY A.author
HAVING (
    SELECT COUNT(B.book_id) 
    FROM authors A 
    INNER JOIN books B ON instr(B.authors, A.author) > 0 
    GROUP BY A.author 
    ORDER BY COUNT(B.book_id) DESC LIMIT 1) - COUNT(B.book_id) > 6
ORDER BY COUNT(B.book_id) DESC;