DROP VIEW borrowings_per_category;
CREATE VIEW IF NOT EXISTS borrowings_per_category AS
SELECT DISTINCT U.name AS name, B.theme_category AS category
FROM bookids_AND_authors_per_category B
INNER JOIN reports R ON instr(B.book_ids, R.book_id) > 0
INNER JOIN users U ON U.user_id = R.user_id
WHERE (R.issue = 'borrowed' OR R.issue = 'returned')
AND strftime('%Y', R.date) = strftime('%Y', date('now'))
AND U.role = 'professor'
GROUP BY U.name, B.theme_category;