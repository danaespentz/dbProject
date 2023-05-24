CREATE VIEW borrowings_per_young_professors AS
SELECT U.name, COUNT(U.name) AS count
FROM users U
INNER JOIN reports R ON U.user_id = R.user_id
WHERE U.age < 40 AND U.role = 'professor'
  AND (R.issue = 'borrowed' OR R.issue = 'returned')
GROUP BY U.name
ORDER BY count DESC;