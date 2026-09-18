from pydantic import BaseModel


class JobSummary(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    work_mode: str | None = None


class JobsResponse(BaseModel):
    jobs: list[JobSummary]
