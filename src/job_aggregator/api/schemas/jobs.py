from pydantic import BaseModel
from datetime import datetime

from pydantic import ConfigDict


class JobSummary(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None


class JobsResponse(BaseModel):
    jobs: list[JobSummary]


class JobDetail(BaseModel):
    id: int
    title: str
    company: str
    location: str | None
    url: str
    description: str | None
    source: str
    published_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
