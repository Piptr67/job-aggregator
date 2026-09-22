from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from job_aggregator.api.schemas.jobs import JobsResponse
from job_aggregator.api.dependencies import get_db

router = APIRouter(prefix="/jobs")


@router.get("", response_model=JobsResponse)
def get_jobs(db: Session = Depends(get_db)) -> JobsResponse:
    return JobsResponse(jobs=[])
