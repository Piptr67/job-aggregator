from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_current_user, get_db
from job_aggregator.api.schemas.jobs import JobDetail, JobsResponse, JobSummary
from job_aggregator.db.models.job import Job
from job_aggregator.db.models.user import User

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobsResponse)
def list_jobs(
    location: str | None = None,
    company: str | None = None,
    q: str | None = Query(default=None, min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobsResponse:
    query = select(Job)

    if location:
        query = query.where(Job.location.icontains(location, autoescape=True))

    if company:
        query = query.where(Job.company.icontains(company, autoescape=True))

    if q:
        search_filter = (
            Job.title.icontains(q, autoescape=True)
            | Job.company.icontains(q, autoescape=True)
            | Job.description.icontains(q, autoescape=True)
        )
        query = query.where(search_filter)

    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0

    jobs = db.scalars(
        query.order_by(Job.published_at.desc().nullslast(), Job.id.desc())
    ).all()

    return JobsResponse(
        jobs=[JobSummary.model_validate(job) for job in jobs],
        total=total,
    )


@router.get("/{job_id}", response_model=JobDetail)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobDetail:
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobDetail.model_validate(job)
