from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_db
from job_aggregator.ingestion.service import ingest_himalayas

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/himalayas")
def trigger_himalayas_ingestion(db: Session = Depends(get_db)) -> dict[str, int]:
    job_count = ingest_himalayas(db)
    return {"jobs_processed": job_count}
