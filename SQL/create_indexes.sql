CREATE INDEX idx_users ON users(user_id, school_id, name);
CREATE INDEX idx_reports ON reports(issue, user_id);
CREATE INDEX idx_books ON books(school_id);