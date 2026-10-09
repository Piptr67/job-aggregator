from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from job_aggregator.api.schemas.jobs import JobsResponse, JobSummary
from job_aggregator.api.dependencies import get_db
from job_aggregator.db.models.job import Job

router = APIRouter(prefix="/jobs")


@router.get("", response_model=JobsResponse)
def get_jobs(
    location: str | None = None,
    company: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
) -> JobsResponse:
    query = select(Job)

    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))

    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))

    if q:
        query = query.where(
            or_(
                Job.title.ilike(f"%{q}%"),
                Job.company.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
            )
        )

    result = db.scalars(query).all()
    jobs = [
        JobSummary(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
        )
        for job in result
    ]

    return JobsResponse(jobs=jobs)


@router.get("/{job_id}", response_model=JobSummary)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobSummary:
    result = db.scalars(select(Job).where(Job.id == job_id)).one_or_none()
    if result is None:
        raise HTTPException(status_code=404)

    job = JobSummary(
        id=result.id,
        title=result.title,
        company=result.company,
        location=result.location,
    )

    return job
