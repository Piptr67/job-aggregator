from collections.abc import Callable

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

SOURCE_REGISTRY: dict[str, Callable[[Session], int]] = {
    "himalayas": ingest_himalayas,
    "arbeitnow": ingest_arbeitnow,
}


@router.post("/{source}")
def trigger_ingestion(
    source: str,
    db: Session = Depends(get_db),
) -> dict[str, int]:
    ingestion_function = SOURCE_REGISTRY.get(source)

    if ingestion_function is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported ingestion source: {source}",
        )

    try:
        job_count = ingestion_function(db)
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch jobs from {source}",
        ) from exc

    return {"jobs_processed": job_count}
