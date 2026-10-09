from sqlalchemy import select
from sqlalchemy.orm import Session

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion.himalayas import ParsedJob, fetch_feed, parse_jobs


def save_job(db: Session, parsed_job: ParsedJob) -> Job:
    result = db.scalars(select(Job).where(Job.url == parsed_job["url"])).first()

    if result is not None:
        return result

    job = Job(
        title=parsed_job["title"],
        company=parsed_job["company"],
        description=parsed_job["description"],
        location=parsed_job["location"],
        url=parsed_job["url"],
        source=parsed_job["source"],
        published_at=parsed_job["published_at"],
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def ingest_himalayas(db: Session) -> int:
    feed = fetch_feed()
    parsed_jobs = parse_jobs(feed)

    for job in parsed_jobs:
        save_job(db, job)

    return len(parsed_jobs)
