from collections.abc import Callable
from enum import StrEnum

import requests
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_current_user, get_db
from job_aggregator.ingestion.service import ingest_arbeitnow, ingest_himalayas

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(get_current_user)],
)


class IngestionSource(StrEnum):
    all = "all"
    himalayas = "himalayas"
    arbeitnow = "arbeitnow"


SOURCE_REGISTRY: dict[IngestionSource, Callable[[Session], int]] = {
    IngestionSource.himalayas: ingest_himalayas,
    IngestionSource.arbeitnow: ingest_arbeitnow,
}


@router.post("/{source}")
def trigger_ingestion(
    source: str = Path(
        ...,
        enum=[source.value for source in IngestionSource],
    ),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    try:
        selected_source = IngestionSource(source)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported ingestion source: {source}",
        ) from exc

    source_names = (
        list(SOURCE_REGISTRY)
        if selected_source == IngestionSource.all
        else [selected_source]
    )

    total_processed = 0
    failures: list[str] = []

    for source_name in source_names:
        ingestion_function = {
            IngestionSource.himalayas: ingest_himalayas,
            IngestionSource.arbeitnow: ingest_arbeitnow,
        }[source_name]

        try:
            total_processed += ingestion_function(db)
        except requests.RequestException:
            failures.append(source_name.value)

    if failures:
        raise HTTPException(
            status_code=502,
            detail={
                "jobs_processed": total_processed,
                "failed_sources": failures,
            },
        )

    return {"jobs_processed": total_processed}
