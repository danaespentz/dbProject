CREATE VIEW loans_per_admin AS
SELECT strftime('%Y', R.date) AS year, S.school_name, U.name, COUNT(R.school_id) AS count
FROM reports R
INNER JOIN schools S ON S.school_id = R.school_id
INNER JOIN users U ON U.user_id = S.admin_id
WHERE R.issue = 'borrowed' OR R.issue = 'returned'
GROUP BY year, R.school_id
HAVING COUNT(R.school_id) > 20
ORDER BY year DESC;

SELECT L.year, L.school_name, L.name, L.count
FROM loans_per_admin L
WHERE L.count IN (
  SELECT count
  FROM loans_per_admin
  GROUP BY count, year
  HAVING COUNT(*) > 1
)
ORDER BY L.count DESC;