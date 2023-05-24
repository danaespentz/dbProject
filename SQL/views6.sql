CREATE VIEW book_ids_per_category AS
SELECT DISTINCT A.theme_category AS category, B.book_id AS book_id
FROM bookids_AND_authors_per_category A
INNER JOIN books B ON instr(A.book_ids, B.book_id) > 0
INNER JOIN reports R ON R.book_id = B.book_id
WHERE (R.issue = 'borrowed' OR R.issue = 'returned')
GROUP BY A.theme_category, B.book_id;

CREATE VIEW common_book_ids_per_category_pair AS
SELECT category1, category2, COUNT(*) AS common_book_count
FROM (
  SELECT DISTINCT A.category AS category1, B.category AS category2, B.book_id AS book_id
  FROM book_ids_per_category A
  INNER JOIN book_ids_per_category B ON A.book_id = B.book_id AND A.category < B.category
) AS pairs
GROUP BY category1, category2
ORDER BY common_book_count DESC;

SELECT category1, category2, common_book_count
FROM common_book_ids_per_category_pair
LIMIT 3;