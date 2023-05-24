CREATE VIEW borrowings_per_school AS
SELECT S.school_id, R.date
FROM schools S
INNER JOIN reports R ON S.school_id = R.school_id
WHERE R.issue = 'borrowed' OR R.issue = 'returned';