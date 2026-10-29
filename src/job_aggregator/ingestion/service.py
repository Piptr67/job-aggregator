from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion import arbeitnow, himalayas
from job_aggregator.ingestion.schemas import ParsedJob


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

    inserted_ids = db.scalars(statement).all()
    db.commit()
    return len(inserted_ids)


def ingest_himalayas(db: Session) -> int:
    feed = himalayas.fetch_feed()
    parsed_jobs = himalayas.parse_jobs(feed)
    return save_jobs(db, parsed_jobs)


def ingest_arbeitnow(db: Session) -> int:
    data = arbeitnow.fetch_jobs()
    parsed_jobs = arbeitnow.parse_jobs(data)
    return save_jobs(db, parsed_jobs)
