import sqlite3
from dataclasses import asdict

from job import Job

DB_NAME = "jobs.db"

CREATE_JOBS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        link TEXT NOT NULL UNIQUE,
        pub_date TEXT,
        company TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

INSERT_JOBS_SQL = """
    INSERT OR IGNORE INTO jobs (
    title,
    description,
    link,
    pub_date,
    company
    )
    VALUES (:title, :description, :link, :pub_date, :company)
"""

GET_JOBS_SQL = """
SELECT title, description, link, pub_date, company
FROM jobs
ORDER BY id DESC
LIMIT ?;
"""

def get_connection(db_name: str = DB_NAME) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_name: str = DB_NAME) -> None:
    with get_connection() as connection:
        connection.execute(CREATE_JOBS_TABLE_SQL)

def save_jobs(jobs: list[Job], db_name: str = DB_NAME) -> int:
    job_dicts = [asdict(job) for job in jobs]
    with get_connection(db_name) as conn:
        cursor = conn.executemany(INSERT_JOBS_SQL, job_dicts)
        return cursor.rowcount

def get_jobs(limit: int = 50, db_name: str = DB_NAME) -> list[Job]:
    with get_connection(db_name) as conn:
        rows = conn.execute(GET_JOBS_SQL, (limit,)).fetchall()

    return [Job(**row) for row in rows]