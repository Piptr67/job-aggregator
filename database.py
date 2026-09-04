import sqlite3

from job import Job
from exceptions import DatabaseError

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
title, description, link, pub_date, company
)
VALUES (:title, :description, :link, :pub_date, :company)
"""

GET_JOBS_SQL = """
SELECT title, description, link, pub_date, company
FROM jobs
ORDER BY id DESC
LIMIT ?;
"""

SEARCH_JOBS_SQL = """
SELECT title, description, link, pub_date, company
FROM jobs
WHERE title LIKE :query
    OR description LIKE :query
    OR company LIKE :query
ORDER BY id DESC
LIMIT :limit;
"""


def get_connection(db_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name: str) -> None:
    try:
        with get_connection(db_name) as connection:
            connection.execute(CREATE_JOBS_TABLE_SQL)
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {db_name}") from e


def save_jobs(jobs: list[Job], db_name: str) -> int:
    job_dicts = [
        {
            "title": job.title,
            "description": job.description,
            "link": job.link,
            "pub_date": job.pub_date,
            "company": job.company,
        }
        for job in jobs
    ]
    try:
        with get_connection(db_name) as conn:
            cursor = conn.executemany(INSERT_JOBS_SQL, job_dicts)
            return cursor.rowcount
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to save jobs to database: {db_name}") from e


def get_jobs(limit: int, db_name: str) -> list[Job]:
    try:
        with get_connection(db_name) as conn:
            rows = conn.execute(GET_JOBS_SQL, (limit,)).fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to search jobs in database: {db_name}") from e
    return [
        Job(
            title=row["title"],
            description=row["description"],
            link=row["link"],
            pub_date=row["pub_date"],
            company=row["company"],
        )
        for row in rows
    ]


def search_jobs(query: str, limit: int, db_name: str) -> list[Job]:
    try:
        with get_connection(db_name) as conn:
            rows = conn.execute(
                SEARCH_JOBS_SQL,
                {"query": f"%{query}%", "limit": limit},
            ).fetchall()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to get search jobs in database: {db_name}") from e

    return [
        Job(
            title=row["title"],
            description=row["description"],
            link=row["link"],
            pub_date=row["pub_date"],
            company=row["company"],
        )
        for row in rows
    ]