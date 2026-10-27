from datetime import datetime

from pydantic import BaseModel, ConfigDict


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str | None = None


class JobsResponse(BaseModel):
    jobs: list[JobSummary]


class JobDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str | None
    url: str
    description: str | None
    source: str
    published_at: datetime | None
