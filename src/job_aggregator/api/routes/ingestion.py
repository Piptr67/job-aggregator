from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_current_user, get_db
from job_aggregator.ingestion.errors import IngestionError
from job_aggregator.ingestion.service import IngestionSource, ingest

router = APIRouter(
    prefix="/ingestion",
    tags=["ingestion"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/{source}")
def trigger_ingestion(
    source: IngestionSource | Literal["all"],
    db: Session = Depends(get_db),
) -> dict[str, object]:
    try:
        return ingest(source, db)
    except IngestionError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "jobs_inserted": exc.jobs_inserted,
                "failed_sources": exc.failed_sources,
            },
        ) from exc
