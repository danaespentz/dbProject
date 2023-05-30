CREATE VIEW IF NOT EXISTS borrowings_per_school_per_monthYear AS
SELECT strftime('%Y-%m', R.date) AS date, S.school_name, COUNT(*) AS count
FROM schools S
INNER JOIN reports R ON S.school_id = R.school_id
WHERE R.issue = 'borrowed' OR R.issue = 'returned'
GROUP BY strftime('%Y-%m', R.date), S.school_name
ORDER BY date DESC;

CREATE VIEW IF NOT EXISTS borrowings_per_school_per_year AS
SELECT strftime('%Y', R.date) AS date, S.school_name, COUNT(*) AS count
FROM schools S
INNER JOIN reports R ON S.school_id = R.school_id
WHERE R.issue = 'borrowed' OR R.issue = 'returned'
GROUP BY strftime('%Y', R.date), S.school_name
ORDER BY date DESC;