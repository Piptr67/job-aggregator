from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ParsedJob(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)
    description: str | None = None
    location: str | None = None
    url: str = Field(min_length=1)
    source: str
    published_at: datetime | None = None
