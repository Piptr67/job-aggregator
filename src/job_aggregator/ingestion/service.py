from collections.abc import Callable
from enum import StrEnum

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from job_aggregator.db.models.job import Job
from job_aggregator.ingestion import arbeitnow, himalayas
from job_aggregator.ingestion.errors import IngestionError
from job_aggregator.ingestion.schemas import ParsedJob


class IngestionSource(StrEnum):
    himalayas = "himalayas"
    arbeitnow = "arbeitnow"
    all = "all"


IngestionRequest = IngestionSource
Fetcher = Callable[[], object]
SourceIngestor = Callable[[Session], int]


def save_jobs(db: Session, jobs: list[ParsedJob]) -> int:
    if not jobs:
        return 0

    rows_by_url = {job.url: job.model_dump() for job in jobs}
    statement = (
        insert(Job)
        .values(list(rows_by_url.values()))
        .on_conflict_do_nothing(index_elements=["url"])
        .returning(Job.id)
    )

    inserted_ids = db.scalars(statement).all()
    db.commit()
    return len(inserted_ids)


def ingest_himalayas(db: Session) -> int:
    feed = himalayas.fetch_feed()
    return save_jobs(db, himalayas.parse_jobs(feed))


def ingest_arbeitnow(db: Session) -> int:
    data = arbeitnow.fetch_jobs()
    return save_jobs(db, arbeitnow.parse_jobs(data))


SOURCE_REGISTRY: dict[IngestionSource, SourceIngestor] = {
    IngestionSource.himalayas: ingest_himalayas,
    IngestionSource.arbeitnow: ingest_arbeitnow,
}


def ingest(source: IngestionRequest, db: Session) -> dict[str, object]:
    sources = list(SOURCE_REGISTRY) if source == "all" else [IngestionSource(source)]
    total_inserted = 0
    failures: list[str] = []

    for source_name in sources:
        try:
            total_inserted += SOURCE_REGISTRY[source_name](db)
        except IngestionError:
            failures.append(source_name.value)

    if failures:
        raise IngestionError(
            f"Ingestion failed for: {', '.join(failures)}",
            jobs_inserted=total_inserted,
            failed_sources=failures,
        )

    return {"jobs_inserted": total_inserted}
