from fastapi import APIRouter, Depends

from sqlalchemy import select
from sqlalchemy.orm import Session

from job_aggregator.api.schemas.jobs import JobsResponse, JobSummary
from job_aggregator.api.dependencies import get_db
from job_aggregator.db.models.job import Job

router = APIRouter(prefix="/jobs")


@router.get("", response_model=JobsResponse)
def get_jobs(db: Session = Depends(get_db)) -> JobsResponse:
    result = db.scalars(select(Job)).all()
    jobs = [
        JobSummary(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            work_mode=job.work_mode,
        )
        for job in result
    ]

    return JobsResponse(jobs=jobs)
