from fastapi import APIRouter

from job_aggregator.api.schemas.jobs import JobsResponse

router = APIRouter(prefix="/jobs")

@router.get("", response_model=JobsResponse)
def get_jobs() -> JobsResponse:
    return JobsResponse(jobs=[])
