from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from job_aggregator.api.dependencies import get_current_user, get_db
from job_aggregator.api.schemas.jobs import JobDetail, JobsResponse, JobSummary
from job_aggregator.db.models.job import Job

router = APIRouter(prefix="/jobs")


def escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


@router.get("", response_model=JobsResponse, dependencies=[Depends(get_current_user)])
def get_jobs(
    location: str | None = None,
    company: str | None = None,
    q: str | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: Literal["published_at", "title", "company", "id"] = "published_at",
    order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
) -> JobsResponse:
    query = select(Job)

    if location:
        query = query.where(
            Job.location.ilike(f"%{escape_like(location)}%", escape="\\")
        )

    if company:
        query = query.where(Job.company.ilike(f"%{escape_like(company)}%", escape="\\"))

    if q:
        search_term = f"%{escape_like(q)}%"
        query = query.where(
            or_(
                Job.title.ilike(search_term, escape="\\"),
                Job.company.ilike(search_term, escape="\\"),
                Job.description.ilike(search_term, escape="\\"),
            )
        )

    sort_columns = {
        "published_at": Job.published_at,
        "title": Job.title,
        "company": Job.company,
        "id": Job.id,
    }

    sort_column = sort_columns[sort_by]

    if order == "desc":
        query = query.order_by(sort_column.desc().nulls_last(), Job.id.asc())
    else:
        query = query.order_by(sort_column.asc().nulls_last(), Job.id.asc())

    query = query.limit(limit).offset(offset)

    result = db.scalars(query).all()
    jobs = [JobSummary.model_validate(job) for job in result]

    return JobsResponse(jobs=jobs)


@router.get(
    "/{job_id}", response_model=JobDetail, dependencies=[Depends(get_current_user)]
)
def get_job(job_id: int, db: Session = Depends(get_db)) -> JobDetail:
    result = db.scalars(select(Job).where(Job.id == job_id)).one_or_none()

    if result is None:
        raise HTTPException(status_code=404)

    return JobDetail.model_validate(result)
