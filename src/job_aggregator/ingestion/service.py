from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion.arbeitnow import (
    fetch_jobs as fetch_arbeitnow_jobs,
    parse_jobs as parse_arbeitnow_jobs,
)
from job_aggregator.ingestion.himalayas import (
    fetch_feed,
    parse_jobs as parse_himalayas_jobs,
)
from job_aggregator.ingestion.schemas import ParsedJob


def save_job(db: Session, parsed_job: ParsedJob) -> tuple[Job, bool]:
    existing_job = db.scalars(select(Job).where(Job.url == parsed_job.url)).first()

    if existing_job is not None:
        return existing_job, False

    job = Job(
        title=parsed_job.title,
        company=parsed_job.company,
        description=parsed_job.description,
        location=parsed_job.location,
        url=parsed_job.url,
        source=parsed_job.source,
        published_at=parsed_job.published_at,
    )

    db.add(job)
    db.flush()
    return job, True


def save_jobs(db: Session, jobs: list[ParsedJob]) -> int:
    if not jobs:
        return 0

    rows_by_url = {job.url: job.model_dump() for job in jobs}
    rows = list(rows_by_url.values())

    statement = (
        insert(Job)
        .values(rows)
        .on_conflict_do_nothing(index_elements=["url"])
        .returning(Job.id)
    )

    try:
        inserted_ids = db.scalars(statement).all()
        db.commit()
        return len(inserted_ids)
    except Exception:
        db.rollback()
        raise


def ingest_himalayas(db: Session) -> int:
    feed = fetch_feed()
    parsed_jobs = parse_himalayas_jobs(feed)
    return save_jobs(db, parsed_jobs)


def ingest_arbeitnow(db: Session) -> int:
    data = fetch_arbeitnow_jobs()
    parsed_jobs = parse_arbeitnow_jobs(data)
    return save_jobs(db, parsed_jobs)
