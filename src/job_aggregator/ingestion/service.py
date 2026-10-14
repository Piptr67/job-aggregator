from sqlalchemy import select
from sqlalchemy.orm import Session

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion.schemas import ParsedJob
from job_aggregator.ingestion.himalayas import (
    fetch_feed,
    parse_jobs as parse_himalayas_jobs,
)
from job_aggregator.ingestion.arbeitnow import (
    fetch_jobs as fetch_arbeitnow_jobs,
    parse_jobs as parse_arbeitnow_jobs,
)


def save_job(db: Session, parsed_job: ParsedJob) -> tuple[Job, bool]:
    result = db.scalars(select(Job).where(Job.url == parsed_job["url"])).first()

    if result is not None:
        return result, False

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

    return job, True


def save_jobs(db: Session, jobs: list[ParsedJob]) -> int:
    inserted_count = 0
    for job in jobs:
        inserted = save_job(db, job)[1]
        if inserted:
            inserted_count += 1

    return inserted_count


def ingest_himalayas(db: Session) -> int:
    feed = fetch_feed()
    parsed_jobs = parse_himalayas_jobs(feed)

    return save_jobs(db, parsed_jobs)


def ingest_arbeitnow(db: Session) -> int:
    data = fetch_arbeitnow_jobs()
    parsed_jobs = parse_arbeitnow_jobs(data)

    return save_jobs(db, parsed_jobs)
