from typing import TypedDict
from datetime import datetime


class ParsedJob(TypedDict):
    title: str | None
    company: str | None
    description: str | None
    location: str | None
    url: str | None
    source: str
    published_at: datetime | None
