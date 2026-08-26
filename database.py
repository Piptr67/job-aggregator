import sqlite3

create_table_sql = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    link TEXT NOT NULL UNIQUE,
    pub_date TEXT,
    company TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

"""

job = (
    "Test Developer",
    "A test job for SQLite",
    "https://example.com/test-job",
    "Wed, 26 Aug 2026 18:00:00 GMT",
    "Test Company",
)

insert_job_sql = """
INSERT OR IGNORE INTO jobs (title, description, link, pub_date, company)
VALUES (?, ?, ?, ?, ?)
"""


with sqlite3.connect("jobs.db") as connection:
    rows = connection.execute("SELECT * FROM jobs").fetchall()

    for row in rows:
        print(row)