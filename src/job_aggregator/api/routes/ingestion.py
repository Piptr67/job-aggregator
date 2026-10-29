from collections.abc import Callable
from enum import StrEnum
from xml.etree.ElementTree import ParseError

import requests
from fastapi import APIRouter, Depends, HTTPException
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
    source: IngestionSource,
    db: Session = Depends(get_db),
) -> dict[str, int]:
    source_names = list(SOURCE_REGISTRY) if source == IngestionSource.all else [source]

    total_inserted = 0
    failures: list[str] = []

    for source_name in source_names:
        try:
            total_inserted += SOURCE_REGISTRY[source_name](db)
        except requests.RequestException:
            failures.append(source_name.value)
        except (ParseError, ValueError):
            if source_name == IngestionSource.himalayas:
                failures.append(source_name.value)
            else:
                raise

    if failures:
        raise HTTPException(
            status_code=502,
            detail={
                "jobs_inserted": total_inserted,
                "failed_sources": failures,
            },
        )

    return {"jobs_inserted": total_inserted}
